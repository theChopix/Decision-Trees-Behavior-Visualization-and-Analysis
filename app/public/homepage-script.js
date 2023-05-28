const modeSelect = document.querySelector('#visu-mode-select');
const treeIdxInput = document.querySelector('#tree-idx-input');
const instanceIdxInput = document.querySelector('#instance-idx-input');
const featureSelect = document.querySelector('#feature-select');
const markSelect = document.querySelector('#mark-select');
const stringOpSelect = document.querySelector('#string-operation-select');
const constantInput = document.querySelector('#constant-input');
const regexpInput = document.querySelector('#regexp-input');

const oneInstanceDiv = document.querySelector('#instance-idx-div');
const multipleInstanceDiv = document.querySelector('#multiple-opts-div');
const labelsInMultiple = multipleInstanceDiv.querySelectorAll('span');

// Handling form in main visualization
// On One or Multiple mode selection displaying appropriate elements
modeSelect.addEventListener('change', function () {
    var selectedOption = modeSelect.options[modeSelect.selectedIndex].value;
    console.log(selectedOption);
    if (selectedOption === 'general') {
        oneInstanceDiv.style.display = 'none';
        multipleInstanceDiv.style.display = 'none';
    } else if (selectedOption === "one") {
        oneInstanceDiv.style.display = 'flex';
        multipleInstanceDiv.style.display = 'none';
    } else if (selectedOption === "multiple") {
        oneInstanceDiv.style.display = 'none';
        multipleInstanceDiv.style.display = 'flex';
        // featureSelect.style.display = 'flex';
        featureSelect.dispatchEvent(new Event('change'));
    }
});

// Handling form in main visualization (feature operations in Multiple mode)
// If selected string feature (url or query) set appropriate elements visible...
featureSelect.addEventListener('change', function () {
    if (featureSelect.value === 'query' || featureSelect.value === 'url') {
        labelsInMultiple[1].style.display = 'none';
        markSelect.style.display = 'none';

        labelsInMultiple[2].style.display = 'flex';
        stringOpSelect.style.display = 'flex';

        labelsInMultiple[3].style.display = 'none';
        constantInput.style.display = 'none';

        labelsInMultiple[4].style.display = 'flex';
        regexpInput.style.display = 'flex';
    } else {
        labelsInMultiple[1].style.display = 'flex';
        markSelect.style.display = 'flex';

        labelsInMultiple[2].style.display = 'none';
        stringOpSelect.style.display = 'none';

        labelsInMultiple[3].style.display = 'flex';
        constantInput.style.display = 'flex';

        labelsInMultiple[4].style.display = 'none';
        regexpInput.style.display = 'none';
    }
});

const defaultColorSetBttn = document.querySelector('#default-color-setter');
const box1ColorPicker = document.querySelector('#box-1-color');
const box0ColorPicker = document.querySelector('#box-0-color');

// Handling button for setting color pickers to default colors
defaultColorSetBttn.addEventListener('click', function () {
    box1ColorPicker.value = '#F6E8A6';
    box0ColorPicker.value = '#B7BEBE';
});

const displayBttn = document.querySelector('#display-button');
const displayVisuLink = document.querySelector('#get-visualization');
const treeIdxAlert = document.querySelector('#tree-idx-alert');

// Handling display button for main visualization
// Sending data from form to server side '/api/sankey'
displayBttn.addEventListener('click', function () {
    let formData = {};
    formData.visuMode = modeSelect.value;

    formData.params = {};
    formData.params.treeIdx = treeIdxInput.value;
    if (modeSelect.value === 'one') {
        formData.params.instIdx = instanceIdxInput.value;
    } else if (modeSelect.value === 'multiple') {
        formData.params.feature = featureSelect.value;
        if (featureSelect.value === 'query' || featureSelect.value === 'url') {
            formData.params.mark = stringOpSelect.value;
            formData.params.const = regexpInput.value;
        } else {
            formData.params.mark = markSelect.value;
            formData.params.const = constantInput.value;
        }
    };
    formData.params.color1 = box1ColorPicker.value;
    formData.params.color0 = box0ColorPicker.value;

    fetch('/api/sankey', {
        method: 'POST',
        body: JSON.stringify(formData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(responseData => {
            console.log(responseData);
            if (responseData.treeIdx === 1) {
                // When process of visualization went well, click on the link that opens window with visualization created by python script
                displayVisuLink.dispatchEvent(new MouseEvent('click'));
            } else {
                // If not, make the 'alert element of out of range tree index' visible
                treeIdxAlert.style.display = 'flex';
            }

        })
        .catch(error => {
            console.error('Error:', error);
        });
});

// With each change of tree index input, make 'alert element of out of range tree index' invisible
treeIdxInput.addEventListener('change', function () {
    treeIdxAlert.style.display = 'none';
});

const baselineTreeIdxInput = document.querySelector('#baseline-tree-idx-input');
const baselineDisplayBttn = document.querySelector('#baseline-display-button');

const baselineDisplayVisuLink = document.querySelector('#get-baseline-visualization');
const baselineTreeIdxAlert = document.querySelector('#baseline-tree-idx-alert');

// Handling display button for baseline visualization
// Sending data (only tree index) from form to server side /api/cb-native
baselineDisplayBttn.addEventListener('click', function () {
    let formData = {};
    formData.treeIdx = baselineTreeIdxInput.value;

    fetch('/api/cb-native', {
        method: 'POST',
        body: JSON.stringify(formData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(responseData => {
            console.log(responseData);
            if (responseData.treeIdx === 1) {
                // When process of visualization went well, click on the link that opens window with visualization created by python script
                baselineDisplayVisuLink.dispatchEvent(new MouseEvent('click'));
            } else {
                // If not, make the alert element of out of range tree index visible
                baselineTreeIdxAlert.style.display = 'flex';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

// With each change of tree index input, make alert element invisible
baselineTreeIdxInput.addEventListener('change', function () {
    baselineTreeIdxAlert.style.display = 'none';
});
