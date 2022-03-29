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
    let token = getToken(req.body.channel);
    res.send(token);
})

// 插入数据
router.post('/insert', function (req, res) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');
        let user = req.body;
        user.timestamp = new Date().getTime();

        // 如果有相同数据，跳过插入
        db.collection('users').find(user).toArray().then(result => {
            if (result.length === 0) {
                db.collection('users').insertOne(user).finally(() => {
                    conn.close();
                })
            }
        })
        res.send('success');
    })
})

// 获取即时专注度
router.post('/getNow', function (req, res) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');
        let channel = req.body;
        db.collection('users').find(channel).toArray().then(result => {
            let valArr = [];
            for (let i = 0; i < result.length; i++) {
                if (Math.abs(result[i].timestamp - new Date().getTime()) < 5 * 1000) {
                    valArr.push(result[i].value);
                }
            }
            let valAvg = '0';
            if (valArr.length > 0) {
                valAvg = ((valArr.reduce((pre, cur) => pre + cur) / valArr.length + 1) * 25).toString();
            }
            console.log('valAvg: ' + valAvg);
            res.send(valAvg);
        }).then(() => {
            conn.close();
        })
    })
})

module.exports = router;
