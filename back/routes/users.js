var express = require('express');
var router = express.Router();
const MongoClient = require('../db').MongoClient;
const URL = require('../db').URL;

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
