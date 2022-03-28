import torch
from fvcore.nn import parameter_count_table, FlopCountAnalysis
from thop import clever_format
from torch import nn
from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from module import PreNorm, FeedForward, LeFF, Residual, UFO_Attention, Attention, ReAttention
import torch.nn.functional as F


def exists(val):
    return val is not None


def default(val, d):
    return val if exists(val) else d


def pair(t):
    return t if isinstance(t, tuple) else (t, t)


# patch merger class

class PatchMerger(nn.Module):
    def __init__(self, dim, num_tokens_out):
        super().__init__()
        self.scale = dim ** -0.5
        self.norm = nn.LayerNorm(dim)
        self.queries = nn.Parameter(torch.randn(num_tokens_out, dim))

    def forward(self, x):
        x = self.norm(x)
        sim = torch.matmul(self.queries, x.transpose(-1, -2)) * self.scale
        attn = sim.softmax(dim=-1)
        return torch.matmul(attn, x)


class SPT(nn.Module):
    def __init__(self, *, dim, patch_size, channels=3):
        super().__init__()
        patch_dim = patch_size * patch_size * 5 * channels

        self.to_patch_tokens = nn.Sequential(
            Rearrange('b c (h p1) (w p2) -> b (h w) (p1 p2 c)', p1=patch_size, p2=patch_size),
            nn.LayerNorm(patch_dim),
            nn.Linear(patch_dim, dim)
        )

    def forward(self, x):
        shifts = ((1, -1, 0, 0), (-1, 1, 0, 0), (0, 0, 1, -1), (0, 0, -1, 1))
        shifted_x = list(map(lambda shift: F.pad(x, shift), shifts))
        x_with_shifts = torch.cat((x, *shifted_x), dim=1)
        return self.to_patch_tokens(x_with_shifts)


class LSA(nn.Module):
    def __init__(self, dim, heads=8, dim_head=64, dropout=0.):
        super().__init__()
        inner_dim = dim_head * heads
        self.heads = heads
        self.temperature = nn.Parameter(torch.log(torch.tensor(dim_head ** -0.5)))

        self.attend = nn.Softmax(dim=-1)
        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias=False)

        self.to_out = nn.Sequential(
            nn.Linear(inner_dim, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=self.heads), qkv)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.temperature.exp()

        mask = torch.eye(dots.shape[-1], device=dots.device, dtype=torch.bool)
        mask_value = -torch.finfo(dots.dtype).max
        dots = dots.masked_fill(mask, mask_value)

        attn = self.attend(dots)

        out = torch.matmul(attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)


class TransformerLeFF(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, scale=4, depth_kernel=3, dropout=0.):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                Residual(PreNorm(dim, UFO_Attention(dim, heads=heads, dim_head=dim_head, dropout=dropout))),
                Residual(PreNorm(dim, LeFF(dim, scale, depth_kernel)))
            ]))

    def forward(self, x):
        c = list()
        for attn, leff in self.layers:
            x = attn(x)
            cls_tokens = x[:, 0]
            c.append(cls_tokens)
            x = leff(x[:, 1:])
            x = torch.cat((cls_tokens.unsqueeze(1), x), dim=1)
        return x, torch.stack(c).transpose(0, 1)


class Transformer(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, mlp_dim, dropout=0., patch_merge_layer=None,
                 patch_merge_num_tokens=8):
        super().__init__()
        self.layers = nn.ModuleList([])

        self.patch_merge_layer_index = default(patch_merge_layer,
                                               depth // 2) - 1  # default to mid-way through transformer, as shown in paper
        self.patch_merger = PatchMerger(dim=dim, num_tokens_out=patch_merge_num_tokens)
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                PreNorm(dim, ReAttention(dim, heads=heads, dim_head=dim_head, dropout=dropout)),
                PreNorm(dim, FeedForward(dim, mlp_dim, dropout=dropout))
            ]))

    def forward(self, x):
        for index, (attn, ff) in enumerate(self.layers):
            x = attn(x) + x
            x = ff(x) + x
            if index == self.patch_merge_layer_index:
                x = self.patch_merger(x)

        return x


class ViViT(nn.Module):
    def __init__(self, image_size=224, patch_size=16, num_classes=4, num_frames=8, dim=192, depth=4, heads=3,
                 pool='cls',
                 in_channels=3, dim_head=64, dropout=0., emb_dropout=0., scale_dim=4, ):
        super().__init__()

        assert pool in {'cls', 'mean'}, 'pool type must be either cls (cls token) or mean (mean pooling)'

        assert image_size % patch_size == 0, 'Image dimensions must be divisible by the patch size.'
        num_patches = (image_size // patch_size) ** 2
        patch_dim = in_channels * patch_size ** 2
        self.to_patch_embedding = nn.Sequential(
            Rearrange('b t c (h p1) (w p2) -> b t (h w) (p1 p2 c)', p1=patch_size, p2=patch_size),
            nn.Linear(patch_dim, dim),
        )
        self.pos_embedding = nn.Parameter(torch.randn(1, num_frames, num_patches + 1, dim))
        self.space_token = nn.Parameter(torch.randn(1, 1, dim))
        self.space_transformer = Transformer(dim, depth, heads, dim_head, dim * scale_dim, dropout,
                                             patch_merge_num_tokens=8)
        self.temporal_token = nn.Parameter(torch.randn(1, 1, dim))
        self.temporal_transformer = Transformer(dim, depth, heads, dim_head, dim * scale_dim, dropout,
                                                patch_merge_num_tokens=4)

        self.dropout = nn.Dropout(emb_dropout)
        self.pool = pool

        self.mlp_head = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, num_classes)
        )

    def forward(self, x):
        x = self.to_patch_embedding(x)
        b, t, n, _ = x.shape

        cls_space_tokens = repeat(self.space_token, '() n d -> b t n d', b=b, t=t)
        x = torch.cat((cls_space_tokens, x), dim=2)
        x += self.pos_embedding[:, :, :(n + 1)]
        x = self.dropout(x)

        x = rearrange(x, 'b t n d -> (b t) n d')
        x = self.space_transformer(x)
        x = rearrange(x[:, 0], '(b t) ... -> b t ...', b=b)

        cls_temporal_tokens = repeat(self.temporal_token, '() n d -> b n d', b=b)
        x = torch.cat((cls_temporal_tokens, x), dim=1)
        x = self.temporal_transformer(x)

        x = x.mean(dim=1) if self.pool == 'mean' else x[:, 0]

        return self.mlp_head(x)