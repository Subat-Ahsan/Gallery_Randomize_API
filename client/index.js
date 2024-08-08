let apiURL = 'http://127.0.0.1:8000/'
let apiEndpoint = apiURL + 'image'

let qstring = ""
let file_tree_data = {}

let filter_updated = false

var customHeaders = new Headers();
customHeaders.append('pragma', 'no-cache');
customHeaders.append('cache-control', 'no-cache');
var myInit = {
    method: 'GET',
    headers: customHeaders,
};

function fullScreenFunction(){
    container = document.querySelector(".fullScreenImageContainer");
    if (container == null){return;}

    if (container.style.display == "none" || container.style.display == ""){

        container.style.display = "block"
    } else{
        container.style.display = "none"
    }
    
}

function showInformationFunction(){
    container = document.querySelector(".lowerBar");
    if (container == null){return;}

    if (container.style.display == "none" || container.style.display == ""){

        container.style.display = "block"
    } else{
        container.style.display = "none"
    }
    
}

function fetchAndDisplayImage(imageIds) {
    let galleryToggle = document.getElementById("galleryToggle");
    let imageNumber = document.getElementById("imageNumber");
    let headers = ""
    let apiPath = apiEndpoint

    if (filter_updated && galleryToggle.checked){
        imageNumber.value = 1;
    }
    filter_updated =false; 
    if (qstring){
        apiPath += ('?dirs=' + qstring);
    }
    if (galleryToggle.checked){
        if (qstring){
            apiPath += ('&num=' + imageNumber.value);
        } else{
            apiPath += ('?num=' + imageNumber.value);
        }   
    } 

    fetch(apiPath, myInit)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            headers = response.headers
 
            return response.blob()
        })
        .then(blob => {
            if (headers != "") {   
                let text = document.getElementById("lowerBarText")
                pathValue = headers.get("path")
                if (pathValue == undefined){
                    text.innerText = "Error getting data";
                } else{
                    text.innerText = pathValue
                }
                let file_number = headers.get("pos")
                if (file_number == undefined){
                    imageNumber.value = "1"
                } else{
                    imageNumber.value = file_number
                }
            }
            
            const imageUrl = URL.createObjectURL(blob);
            for (i of imageIds){
                let image = document.getElementById(i)     
                if (image != null){
                    image.src = imageUrl
                }
            }
            switchPage('page1')
        })
        .catch(error => {

        });
}

function changeImageNum(incr){
    let input = document.getElementById("imageNumber");
    let new_value = parseInt(input.value) + incr;
    if (new_value > 0){
        input.value = new_value
    } else{
        input.value = 1
    }
}

function updateImageWithNum(incr){
    let galleryToggle = document.getElementById("galleryToggle");
    if (galleryToggle.checked){
        changeImageNum(incr);
        fetchAndDisplayImage(['mainPageImage','fullScreenImage']);
    }
}

function galleryToggleFunction(elem){
    let input = document.getElementById("imageNumber");
    input.disabled = !elem.checked
}

function switchPage(pageId){
    let pages = document.querySelectorAll(".contentPage");
    for (p of pages){
        p.classList.remove('active')
    }
    let page = document.getElementById(pageId)
    page.classList.add('active')
}

function hideList(target_list){
    const children = target_list.children
    let off = target_list.getAttribute("off") === "false" || target_list.getAttribute("off") === null
    target_list.setAttribute("off", off ? "true" : "false")

    for (child of children){
        if (child.nodeName === 'UL'){
            if (off){
                child.classList.add("hidden")
            } else{
                child.classList.remove("hidden")
            }
        }
    }
}
function recursiveListCreate(dir){
    const ul = document.createElement('ul');
    ul.classList.add("queryList");
    const li = document.createElement('li');

    const checkbox = document.createElement("input")
    checkbox.type = "checkbox"

    const span = document.createElement("span")
    
    let col1w = 6;
    let col2w = 40;
    let innerString = 
    ` ${dir.pos ? dir.pos+'.' : ''} ${dir.name} &nbsp;(${dir.count})`
    span.innerHTML = innerString;
    
    
    li.appendChild(checkbox)
    li.appendChild(span)
    ul.appendChild(li)
    ul.setAttribute("pos", `${dir.pos}`)
    span.onclick = function () {hideList(ul) } 

    if (dir["children"] && dir["children"].length > 0){
        for (d of dir["children"].toReversed()){
            const child = recursiveListCreate(d)
            ul.appendChild(child)
    }}
    
    return ul
}

function recursiveResetFilterSelection(elem){
    const children = elem.children;
    for (child of children){
        if (child.nodeName === "LI"){
            box = child.querySelector("input");
            if (box){box.checked = false}
        }
        if (child.nodeName == "UL"){
            recursiveResetFilterSelection(child)
        }
    }
}

function resetFilterSelection(){
    let topList = document.querySelector("#page2 > ul");
    recursiveResetFilterSelection(topList)
}

function updateFilterPage(){
    page = document.getElementById("page2");
    page.innerHTML = "";
    
    if (file_tree_data){
        const elem = recursiveListCreate(file_tree_data)
        page.appendChild(elem)
    }
}

function recursiveUpdateQueryString(string_list,elem,currentPath){
    let new_path = ""
    const children = elem.children;
    pos = elem.getAttribute("pos")
    if (!pos){return;}
    if (pos === "undefined") {
        new_path = ""
    } else{
        new_path = currentPath + pos + "/";
    }
    
    for (child of children){
        if (child.nodeName === "LI"){
            let box = child.querySelector("input");
            if (box){
                if (box.checked == true){
                        string_list.push(new_path)
                    break;
                } else{

                }
            }
        }
        if (child.nodeName == "UL"){
            recursiveUpdateQueryString(string_list,child,new_path)
        }
    }
}

function updateQueryString(){
    let topList = document.querySelector("#page2 > ul");
    let string_list = []
    recursiveUpdateQueryString(string_list,topList,"")
    if (string_list.length == 0){
        qstring = ""
    } else{
        qstring = string_list.toString()
    }
    filter_updated = true
}

document.addEventListener('keydown' , (event) => {
    if (event.key == 'r'){
        fetchAndDisplayImage(['mainPageImage','fullScreenImage'])
    }
    if (event.key == 'f'){
        fullScreenFunction()
    }
    if (event.key == 'i'){
        showInformationFunction()
    }
    if (event.key == 'ArrowRight'){
        updateImageWithNum(1)
    }
    if (event.key == 'ArrowLeft'){
        updateImageWithNum(-1)
    }
})

async function updateFileTreeData(){
    return fetch(apiURL + "data/").then( (response) => {
        if (!response.ok){
            throw new Error("Error getting data: " + response.statusText);
        }
        return response.json();
    }).then ( (data) =>{ 
        file_tree_data = data;
    }) . catch ( (error) => {
        console.log(error)
    })
}

async function main(){
    await updateFileTreeData()
    updateFilterPage()
}

main()