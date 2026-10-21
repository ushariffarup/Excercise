async function getPlaceHolder() {
        const response = await fetch("https://jsonplaceholder.typicode.com/posts/1");
        console.log(await response.json())
        console.log(response.status)
}

getPlaceHolder();
