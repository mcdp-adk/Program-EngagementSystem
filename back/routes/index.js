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
            let now = new Date().getTime();
            for (let i = 0; i < result.length; i++) {
                if (Math.abs(result[i].timestamp - now) < 5 * 1000) {
                    valArr.push(parseInt(result[i].value));
                }
            }
            let valAvg = 0;
            if (valArr.length > 0) {
                for (let i = 0; i < valArr.length; i++) {
                    valAvg += valArr[i];
                }
                valAvg = (valAvg / valArr.length + 1) * 25;
            }
            console.log('valAvg: ' + valAvg);
            res.send(valAvg.toString());
        }).then(() => {
            conn.close();
        })
    })
})

// 下课 & 整理专注度数据
router.post('/stopClass', function (req, res) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');
        let channel = req.body;
        let uname = new Set();
        let data = {
            channel: channel.channel,
            value: '',
            startTime: undefined,
            endTime: undefined
        };

        // 整体专注度数据
        db.collection('users').find(channel).toArray().then(result => {
            if (result.length > 0) {
                // 查找最早时间戳与最晚时间戳
                data.startTime = result[0].timestamp;
                data.endTime = result[0].timestamp;
                for (let i = 0; i < result.length; i++) {
                    if (result[i].timestamp < data.startTime) {
                        data.startTime = result[i].timestamp;
                    }
                    if (result[i].timestamp > data.endTime) {
                        data.endTime = result[i].timestamp;
                    }
                    uname.add(result[i].uname);
                }
                data.value += data.startTime + ',' + data.endTime + ',';

                // 获取每隔 1min 的平均专注度
                for (let time = new Date(data.startTime).getTime(); time < data.endTime; time += 1000 * 60) {
                    let valArr = [];
                    for (let i = 0; i < result.length; i++) {
                        if (result[i].timestamp - time < 1000 * 60 && result[i].timestamp - time > 0) {
                            valArr.push(parseInt(result[i].value));
                        }
                    }
                    let valAvg = 0;
                    if (valArr.length > 0) {
                        for (let i = 0; i < valArr.length; i++) {
                            valAvg += valArr[i];
                        }
                        valAvg = (valAvg / valArr.length + 1) * 25;
                    }
                    data.value += valAvg + ',';
                }
                data.value = data.value.substring(0, data.value.length - 1);

                // 插入新数据库
                db.collection(data.channel).insertOne(data);

                // 插入个人数据
                uname.forEach(item => {
                    let user = {
                        uname: item,
                        value: ''
                    };

                    for (let time = new Date(data.startTime).getTime(); time < data.endTime; time += 1000 * 60) {
                        let valArr = [];
                        for (let i = 0; i < result.length; i++) {
                            if (result[i].timestamp - time < 1000 * 60 && result[i].timestamp - time > 0 && result[i].uname === item) {
                                valArr.push(parseInt(result[i].value));
                            }
                        }
                        let valAvg = 0;
                        if (valArr.length > 0) {
                            for (let i = 0; i < valArr.length; i++) {
                                valAvg += valArr[i];
                            }
                            valAvg = (valAvg / valArr.length + 1) * 25;
                        }
                        user.value += valAvg + ',';
                    }
                    user.value = user.value.substring(0, user.value.length - 1);

                    db.collection(data.channel).insertOne(user);
                })
            }
        }).then(() => {
            // 删除原数据
            db.collection('users').deleteMany(channel);
        })
        res.send('success');
    })
})

// 获取整理后的全部数据
router.post('/getAllData', function (req, res) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');
        let channel = req.body;

        db.collection(channel.channel).find(channel).toArray().then(result => {
            res.send(result[0].value);
        }).then(() => {
            conn.close();
        })
    })
})

// 获取整理后的个人数据
router.post('/getUserData', function (req, res) {
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');
        let user = {uname: req.body.uname};

        db.collection(req.body.channel).find(user).toArray().then(result => {
            res.send(result[0].value);
        }).then(() => {
            conn.close();
        })
    })
})

// 获取整理后的所有个人数据
router.post('/getAllUserData', function (req, res) {
    console.log(req.body);
    MongoClient.connect(URL, function (err, conn) {
        let db = conn.db('engagementSystem');

        db.collection(req.body.channel).find({}).toArray().then(result => {
            res.json(result);
        }).then(() => {
            conn.close();
        })
    })
})

module.exports = router;
