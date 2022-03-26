var express = require('express');
var router = express.Router();
const MongoClient = require('../db').MongoClient;
const URL = require('../db').URL;
const {RtcTokenBuilder, RtmTokenBuilder, RtcRole, RtmRole} = require('agora-access-token');

function getToken(channelName) {
    const appID = '8aaf87961df2495d97f7497e553e8817';
    const appCertificate = '150645edc95145298117937e03c8a7a1';
    const uid = 0;
    const role = RtcRole.PUBLISHER;

    let expirationTimeInSeconds = 7200;
    let currentTimestamp = Math.floor(Date.now() / 1000);
    let privilegeExpiredTs = currentTimestamp + expirationTimeInSeconds;

    // IMPORTANT! Build token with either the uid or with the user account. Comment out the option you do not want to use below.

    // Build token with uid
    let token = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, uid, role, privilegeExpiredTs);

    console.log("channelName: " + channelName);
    console.log("token: " + token);
    return token;
}

/* GET home page. */
router.get('/', function (req, res, next) {
    res.render('index', {title: 'Express'});
});

// 获取 Token
router.post('/token', function (req, res) {
    res.send(getToken(req.body.channel));
})

// 插入数据
router.post('/insert', function (req, res) {
    req.send('uname=' + req.body.uname + '&channel=' + req.body.channel + '&role=' + req.body.role + '&timestamp=' + req.body.timestamp + '&value=' + req.body.value);
})

module.exports = router;
