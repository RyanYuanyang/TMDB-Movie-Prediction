const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const gitApi = require("./routes/api");

const cors = require('cors');

app.use(bodyParser.json());
app.use(cors());

app.use(function(req,res,next){
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.setHeader('Access-Control-Allow-Origin', 'X-Requested-With,content-type');
    res.setHeader('Access-Control-Allow-Credentials', true);

    next();
})

app.use('/api', gitApi);
app.get('/', function(req, res){
    res.send('Server is up and running!')
});

app.listen(3000, function(){
    console.log('Server is listening');
})