const Promise = require("bluebird");
const express = require('express');
const router = express.Router();
const fs = require('fs');
const fetch = require('node-fetch');
// const { Octokit, App } = require("octokit");
// const octokit = new Octokit({
//   auth: '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'
// });

function saveCSVToFile(csvData, filePath) {
  fs.writeFile(filePath, csvData, 'utf8', (err) => {
    if (err) {
      console.error('Error saving CSV file:', err);
    } else {
      console.log('CSV file saved successfully!');
    }
  });
}

function convertArrayOfObjectsToCSV(data) {
  const csvRows = [];
  const headers = Object.keys(data[0]);

  // Add headers to CSV
  csvRows.push(headers.join(','));

  // Convert each object to a CSV row
  for (const row of data) {
    const values = headers.map(header => {
      let value = row[header];

      // If the value is an array of objects, convert it to a raw string
      if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'object') {
        value = "\"[" + value.map(obj => JSON.stringify(obj).replaceAll("\"", "'")).join(',') + "]\"";
      }
      else if(typeof value === 'object'){
        value = "\"[" + JSON.stringify(value).replaceAll("\"", "'") + "]\"";
      }else if (header === 'overview' | header === 'original_title' | header === 'title' | header === 'tagline'){
        value = `"${value.replaceAll("\"", "'")}"`
      }

      return value;
    });
    csvRows.push(values.join(','));
  }

  // Join rows with line breaks to form the CSV content
  const csvContent = csvRows.join('\n');
  return csvContent;
}

function filt(raw, fields){

    let filtered = raw.map((obj_raw)=>
        fields.reduce((obj, key)=>{
            if (key[1] === "login"){
                if (obj_raw["author"] === null){
                    obj["author"] = obj_raw["commit"]["author"]["name"];
                }else{
                    obj["author"] = obj_raw["author"]["login"];
                }
                return obj;
            }
            if (key.length === 2){
                obj[key[1]] = obj_raw[key[0]][key[1]];
                return obj;
            }
            if (key === "files"){
                obj["files"] = filt(obj_raw["files"], ["filename", "additions", "deletions", "changes", "status"]);
                return obj
            }
            if (key === "stats"){
                obj["total_changes"] = obj_raw[key]["total"];
                obj["total_lines_added"] = obj_raw[key]["additions"];
                obj["total_lines_deleted"] = obj_raw[key]["deletions"];
                return obj;
            }
            if (key === "date"){
                let date = new Date(obj_raw["commit"]["committer"]["date"]);
                obj["commit_date"] = date;
            }
    
            obj[key] = obj_raw[key];
            return obj;
        },{})
    )
    
    return filtered
}

// write an endpoint to call /tmdb/popular multiple times
// and save the results to a CSV file

router.get('/tmdb', async function(req, res){
    // write an endpoint to call /tmdb/popular multiple times
    // and save the results to a CSV file
    result = []
    for (let i = 0; i < 3; i++){
        const url = `http://localhost:3000/api/tmdb/popular?start=${i*10+1}`
        const options = {
            method: 'GET',
            // accept array of objects
            headers: {
                accept: 'application/json'
            }
        };
        let res = await fetch(url, options)
            .then(res => res.json())
            .catch(err => console.error('error:' + err))
            console.log(res[0])
        // concat the result
        result = result.concat(res)
        let csv = convertArrayOfObjectsToCSV(result)
        saveCSVToFile(csv,  `${i}.csv`)
        await Promise.delay(2000)
    }
    res.send(result)
    
})

router.get('/tmdb/popular', async function(req, res){
    // get params from request header
    const start = parseInt(req.query.start);
    // string to int
    let list = []
    let requests = []

    for (let i = start; i < (start + 10); i++){
        const url = `https://api.themoviedb.org/3/movie/popular?language=en-US&page=${i}`;
        const options = {
            method: 'GET',
            headers: {
                accept: 'application/json',
                Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZDM1ZGIxMmUzNzY2MzNlNmM4MjQ2ZmI0NjJkZTdkNCIsInN1YiI6IjY1NTRjNGI4NTM4NjZlMDExYzA3MWVhMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nEd9N0ug4OYd8262DGD1fYNupsbY-v-t5RmcEG4CSx8'
            }
        };
      
        requests.push(
            fetch(url, options)
            .then(res => {                
                return res.json()})
            .then(json => {
                result = json["results"].map(movie => movie["id"])
                return result
            })
            .catch(err => console.error('error:' + err))
        )
    }
    list = await Promise.all(requests)
        .then((results) => {
            list = results.flat(); // Flatten the array of results
            return list
        })
        .catch((err) => {
            console.error('error:' + err);
            res.send([]);
        });
   
    let requests2 = []
    for (id of list){
        const url = `https://api.themoviedb.org/3/movie/${id}?language=en-US`;
        const options = {
            method: 'GET',
            headers: {
                accept: 'application/json',
                Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZDM1ZGIxMmUzNzY2MzNlNmM4MjQ2ZmI0NjJkZTdkNCIsInN1YiI6IjY1NTRjNGI4NTM4NjZlMDExYzA3MWVhMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nEd9N0ug4OYd8262DGD1fYNupsbY-v-t5RmcEG4CSx8'
            }
        };
      
        requests2.push(
            fetch(url, options)
            .then(res => {
                res_json = res.json()
                return res_json
            })
            .catch(err => console.error('error:' + err))
        )
    }
    let final = await Promise.all(requests2)
        .then((results) => {
            list = results.flat(); // Flatten the array of results
            return list
        })
        .catch((err) => {
            console.error('error:' + err);
            res.send([]);
        });
    let final2 = await Promise.map(final, async (movie)=>{
        if (movie){
            const url_cretits = `https://api.themoviedb.org/3/movie/${movie["id"]}/credits?language=en-US`
            const options_credits = {
                method: 'GET',
                headers: {
                    accept: 'application/json',
                    Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZDM1ZGIxMmUzNzY2MzNlNmM4MjQ2ZmI0NjJkZTdkNCIsInN1YiI6IjY1NTRjNGI4NTM4NjZlMDExYzA3MWVhMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nEd9N0ug4OYd8262DGD1fYNupsbY-v-t5RmcEG4CSx8'
                }
            }  
            let credits = await fetch(url_cretits, options_credits)
                .then(res => res.json())
                .then(json => {
                    return json
                })
                .catch(err => console.error('error:' + err))
            // return cast with only their names, cast_id, character, credit_id, gender, id, order, profile_path
           
            
            
            movie["cast"] = credits["cast"].map((cast)=>{
                return {
                    id: cast["id"],
                    order: cast["order"],
                    character: cast["character"],
                    gender: cast['gender'],
                    name: cast["name"],
                }})
           
            movie["cast_num"] = credits["cast"].length
            movie["crew"] = credits["crew"].map((crew)=>{
                return {
                    id: crew["id"],
                    job: crew["job"],
                    name: crew["name"],
                    gender: crew["gender"],
                }
            }).filter((crew)=>{
                return crew["job"] === "Director" | crew["job"] === "Producer" | crew["job"] === "Executive Producer" | crew["job"] === "Composer" | crew["job"] === "Director of Photography" | crew["job"] === "Editor"
            })
            movie["crew_num"] = credits["crew"].length
            // movie["num_male_crew"] = credits["crew"].filter((crew)=>{
            //     return crew["gender"] === 2
            // }).length
            // movie["num_female_crew"] = credits["crew"].filter((crew)=>{
            //     return crew["gender"] === 1
            // }).length
            // the length of crew
            return movie
        }
    })
    // print type of final2
    let csv = convertArrayOfObjectsToCSV(final2)
    saveCSVToFile(csv, `${start}-${start+10}.csv`)
    res.send(final2)
})


router.get('/github/repoinfo/:owner', async function(req, res){
    const owner = req.params.owner;
    try{
        raw = [];
        for (let i = 1; i < 31; i++){
            let name = 'Hackathon-gp' + i;
            apiRes = await octokit.request('GET /repos/{owner}/{repo}/commits', {
                owner: owner,
                repo: name,
                headers: {
                    'X-GitHub-Api-Version': '2022-11-28'
                }
            })
            let commit_raw = apiRes.data;
            let shas = filt(commit_raw, ["sha"]);
            let final = await Promise.map(shas, async (sha)=>{
                let commitRes = await octokit.request('GET /repos/{owner}/{repo}/commits/{sha}', {
                    owner: owner,
                    repo: name,
                    sha: sha.sha,
                    headers: {
                        'X-GitHub-Api-Version': '2022-11-28'
                    }
                })
                let commentsRes = await octokit.request('GET /repos/{owner}/{repo}/commits/{sha}/comments', {
                    owner: owner,
                    repo: name,
                    sha: sha.sha,
                    headers: {
                        'X-GitHub-Api-Version': '2022-11-28'
                    }
                })
                commitRes.data['commit_id'] = sha.sha;
                commitRes.data['comments'] = [];
                if (commentsRes.data.length > 0){
                    commentsRes.data.map((comment)=>{
                        commitRes.data['comments'] += (comment.user.login + ': ' + comment.body + '\n');
                    })
                }else{
                    commitRes.data['comments']+=("");
                }
                return commitRes.data;
            });
            
            let filtered_final = filt(final, ["commit_id", ["author", "login"], "date", ["commit", "message"], "stats", "files","comments"]);
            let repo = {repoName: name, commits: filtered_final.filter((obj)=>obj["author"] !== "RyanYuanyang")};
            raw.push(repo);        
        }
        // res.send(raw)
        raw = raw.filter((gp)=>{
            return gp["commits"].length
        })

        let timed = raw.map((gp)=>{
            if (!gp["commits"].length){
                return gp
            }else{
                let dates = gp["commits"].reduce((groups, commit)=>{
                    let date = commit["commit_date"].toISOString().split('T')[0];
                    if (!groups[date]) {
                        groups[date] = {number_of_commits: 0, files_changed:0, total_lines_changed:0, contributors:""};
                    }
                    groups[date]["number_of_commits"] += 1;
                    groups[date]["total_lines_changed"] += commit["total_changes"];
                    groups[date]["files_changed"] += commit["files"].length;
                    if (!groups[date]["contributors"].includes(commit["author"])){

                        groups[date]["contributors"] += (groups[date]["contributors"] === "")?(commit["author"]):(" | "+commit["author"])
                    }
                    return groups
                },{})
                let datesArr = Object.keys(dates).map((date)=>{
                    return{
                        date,
                        stats:dates[date]
                    }
                })
                gp["commits"] = datesArr
                return gp
            }
        })

        res.send(timed);
    } catch (error){
        console.log(error);
        res.send("Oops, something went wrong");
    }
})

module.exports = router;
