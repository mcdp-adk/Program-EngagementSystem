var express = require('express');
var router = express.Router();
const MongoClient = require('../db').MongoClient;
const URL = require('../db').URL;
const {RtcTokenBuilder, RtmTokenBuilder, RtcRole, RtmRole} = require('agora-access-token');

router.get('/', function (req, res) {
    const appID = '8aaf87961df2495d97f7497e553e8817';
    const appCertificate = '150645edc95145298117937e03c8a7a1';
    const channelName = 'test';
    const uid = 0;
    const account = "0";
    const role = RtcRole.PUBLISHER;

    const expirationTimeInSeconds = 3600

    const currentTimestamp = Math.floor(Date.now() / 1000)

    const privilegeExpiredTs = currentTimestamp + expirationTimeInSeconds

    // IMPORTANT! Build token with either the uid or with the user account. Comment out the option you do not want to use below.

    // Build token with uid
    const tokenA = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, uid, role, privilegeExpiredTs);
    console.log("Token With Integer Number Uid: " + tokenA);

    // Build token with user account
    const tokenB = RtcTokenBuilder.buildTokenWithAccount(appID, appCertificate, channelName, account, role, privilegeExpiredTs);
    console.log("Token With UserAccount: " + tokenB);

    res.send('/');
})

// 插入数据
router.post('/insert', function (req, res, next) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');

        // 如果有相同数据，跳过插入
        db.collection('users').find(req.body).toArray().then(result => {
            if (result.length === 0) {
                db.collection('users').insertOne(req.body)
                    .then(() => {
                        res.send('1');
                    })
                    .finally(() => {
                        conn.close();
                    })
            } else {
                res.send('0');
            }
        })
    })
});

module.exports = router;
