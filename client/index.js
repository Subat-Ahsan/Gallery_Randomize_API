const apiEndpoint = 'http://127.0.0.1:8000/image'
const qstring = ""

var myHeaders = new Headers();
    myHeaders.append('pragma', 'no-cache');
    myHeaders.append('cache-control', 'no-cache');
    var myInit = {
        method: 'GET',
        headers: myHeaders,
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

function fetchAndDisplayImage(imageIds) {
  
    fetch(apiEndpoint+qstring, myInit)
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
        })
        .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        for (i of imageIds){
            image = document.getElementById(i)     
            if (image != null){
                image.src = imageUrl
            }
        }
        })
        .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
        });
}



document.addEventListener('keydown' , (event) => {
    if (event.key == 'r'){
        fetchAndDisplayImage(['mainPageImage','fullScreenImage'])
    }
    if (event.key == 'f'){
        fullScreenFunction()
    }
})
