const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.set('view engine', 'ejs');
app.use(express.json());
app.use(express.static('public'));

const path = require('path');
const readline = require('readline');

function allElementsInList1AreInList2(list_1, list_2) {
    return list_1.every((element) => list_2.includes(element));
};

function removeElementFromArray(arr, elementToRemove) {
    return arr.filter((element) => element !== elementToRemove);
};

// Landing page function checking the required files and rendering the homepage.ejs
app.get('/', function (req, res) {
    const modelFilePath = path.join(__dirname, 'data', 'model.json');
    const dataFilePath = path.join(__dirname, 'data', 'validation-set.tsv');

    let modelFeatures;
    let dataFeatures;

    // Check if model.json file exists
    if (fs.existsSync(modelFilePath)) {

        // Try to get feature names from model.json
        try {
            const fileDataJSON = JSON.parse(fs.readFileSync(modelFilePath, 'utf-8'));

            modelFeatures = [];
            for (let i = 0; i < fileDataJSON.features_info.float_features.length; i++) {
                modelFeatures.push(fileDataJSON.features_info.float_features[i].feature_name);
            }
            console.log(modelFeatures);

            const maxTreeIdx = fileDataJSON.oblivious_trees.length - 1

            // Check if validation-set.tsv file exists
            if (fs.existsSync(dataFilePath)) {

                // Try to get feature names from validation-set.tsv
                try {
                    const fileStream = fs.createReadStream(dataFilePath);
                    const rl = readline.createInterface({
                        input: fileStream,
                        crlfDelay: Infinity,
                    });

                    rl.once('line', (firstLine) => {
                        rl.close();
                        dataFeatures = firstLine.split('\t');

                        console.log(dataFeatures);

                        // Check if all feature names from model.json are in validation-set.tsv
                        if (allElementsInList1AreInList2(modelFeatures, dataFeatures)) {
                            let featuresArray = removeElementFromArray(dataFeatures, "box");
                            res.render('homepage.ejs', { loadingError: 0, featuresArray: featuresArray, maxTreeIdx: maxTreeIdx });
                        } else {
                            // If model.json consists of features that are not in validation-set.tsv, send appropriate number of loading error (5)
                            res.render('homepage.ejs', { loadingError: 5, featuresArray: [], maxTreeIdx: maxTreeIdx });
                            console.log('Loading Error no. 5 occured.');
                        };
                    });

                } catch (error) {
                    // If it failed to get feature names from model.json send appropriate number of loading error (4)
                    res.render('homepage.ejs', { loadingError: 4, featuresArray: [], maxTreeIdx: maxTreeIdx });
                    console.log('Loading Error no. 4 occured.');
                }

            } else {
                // If validation-set.tsv file doesn't exist send appropriate number of loading error (3)
                res.render('homepage.ejs', { loadingError: 3, featuresArray: [], maxTreeIdx: maxTreeIdx });
                console.log('Loading Error no. 3 occured.');
            };

        } catch (error) {
            // If it failed to get feature names from model.json send appropriate number of loading error (2)
            res.render('homepage.ejs', { loadingError: 2, featuresArray: [], maxTreeIdx: 0 });
            console.log('Loading Error no. 2 occured.');
        };

    } else {
        // If model.json file doesn't exist send appropriate number of loading error (1)
        res.render('homepage.ejs', { loadingError: 1, featuresArray: [], maxTreeIdx: 0 });
        console.log('Loading Error no. 1 occured.');
    };
});

// Post function for handling the main visualization 
// Receiving form parametres from frontend & executing appropriate python script
app.post('/api/sankey', function (req, res) {
    const formData = req.body;
    console.log(formData);

    try {
        const fileDataJSON = JSON.parse(fs.readFileSync('data/model.json', 'utf-8'));
        const maxTreeIdx = fileDataJSON.oblivious_trees.length - 1

        // Check if given tree index is in correct range
        if (formData.params.treeIdx < 0 || formData.params.treeIdx > maxTreeIdx) {
            res.json({ treeIdx: -1 });
        } else {
            if (formData.visuMode === 'general') {
                const pythonProcess = spawn('python3', ['python/general.py', formData.params.treeIdx, formData.params.color1, formData.params.color0]);
                pythonProcess.on('close', (code) => {
                    console.log(`child process exited with code ${code}`);
                    res.json({ treeIdx: 1 });
                });
            } else if (formData.visuMode === 'one') {
                const pythonProcess = spawn('python3', ['python/one.py', formData.params.treeIdx, formData.params.instIdx, formData.params.color1, formData.params.color0]);
                pythonProcess.on('close', (code) => {
                    console.log(`child process exited with code ${code}`);
                    res.json({ treeIdx: 1 });
                });
            } else if (formData.visuMode === 'multiple') {
                const pythonProcess = spawn('python3', ['python/multiple.py', formData.params.treeIdx, formData.params.feature, formData.params.mark, formData.params.const, formData.params.color1, formData.params.color0]);
                pythonProcess.on('close', (code) => {
                    console.log(`child process exited with code ${code}`);
                    res.json({ treeIdx: 1 });
                });
            }
        }
    } catch (error) {
        console.log(error);
    }
});

// Post function for handling the baseline visualization 
// Receiving form parameter (tree index) from frontend & executing python script
app.post('/api/cb-native', function (req, res) {
    const formData = req.body;
    console.log(formData);

    try {
        const fileDataJSON = JSON.parse(fs.readFileSync('data/model.json', 'utf-8'));
        const maxTreeIdx = fileDataJSON.oblivious_trees.length - 1

        // Check if given tree index is in correct range
        if (formData.treeIdx < 0 || formData.treeIdx > maxTreeIdx) {
            console.log('invalid range of tree index');
            res.json({ treeIdx: -1 });
        } else {
            const pythonProcess = spawn('python3', ['python/cb-native.py', formData.treeIdx]);
            pythonProcess.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                res.json({ treeIdx: 1 });
            });
        }
    } catch (error) {
        console.log(error);
    }
});

app.listen(3000, () => console.log('Decision tree visualization NodeJS app is running on port 3000'));
