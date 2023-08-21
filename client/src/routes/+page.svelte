<title>ImfitTre</title>

<script>
    import { JsonView } from '@zerodevx/svelte-json-view';
    
    let autoload = false;
    let date = new Date().toISOString().substring(0, 10);
    let shotNumber = "";

    let shotData = {};

    async function loadShotData() {
        const response = await fetch('https://jsonplaceholder.typicode.com/todos');
        shotData = await response.json();
    }

    // load data on page load
    loadShotData();

    function handleLoad() {
        if (autoload) {
            loadShotData();
        } else {
            console.log(`Loading shot ${shotNumber} from ${date}`);
        }
    }
    
    /** @type {Array<Record<string, any>>} */
    let images = [];
    for (let i = 0; i < 5; i++) {
        const element = {
            url: 'https://chefsmandala.com/wp-content/uploads/2018/03/Crab.jpg',
            metadata: {
                title: 'Image ' + i,
                description: 'This is image ' + i
            }
        };
        images.push(element);
    }
</script>

<style>
    .image-container {
        display: inline-block;
        width: 90%;
        margin-bottom: 10px;
        border: 1px solid black;
        padding: 10px;
    }

    .image {
        width: 100%;
        margin-bottom: 10px;
        image-rendering: pixelated;
    }

    .metadata {
        display: flex;
        flex-direction: column;
    }

    .sidenav {
        height: 100%; /*Full-height: remove this if you want "auto" height */
        width: 33%; /*Set the width of the sidebar*/
        position: fixed; /* Fixed Sidebar (stay in place on scroll) */
        z-index: 1; /* Stay on top */
        top: 0; /* Stay at the top */
        left: 0;
        background-color: #ffffff;
        overflow-x: hidden; /* Disable horizontal scroll */
        padding-top: 20px;
    }

    .sidenav form {
        display: flex;
        flex-direction: row;
        align-items:center;
        justify-content: left;
        flex-wrap: wrap;
    }

    .sidenav label {
        margin-bottom: 10px;
        margin-left: 10px;
        color: #000000;
    }

    .sidenav input {
        margin-left: 10px;
        width: min-content;
    }

    .main {
        margin-left: 33%; /* Same as the width of the sidebar */
        padding: 0px 10px;
    }
</style>

<nav class="sidenav" style="display: flex; flex-direction: column;">
    <h1 style="display: flex; align-items: center;">
        <img src="small_krab.png" alt="Logo" style="height: 48px; margin-right: 0.5em; margin-left: 10px">
        <span style="margin-right: 20px; font-size: 48px; font-family: 'Comic Sans MS', cursive, sans-serif;">ImfitTre</span>
    </h1>
    <form>
        <label>
            Autoload:
            <input type="checkbox" bind:checked={autoload} />
        </label>
        <label>
            Date:
            <input type="date" bind:value={date} disabled={autoload} on:change={loadShotData} />
        </label>
        <label>
            Shot:
            <input type="number" bind:value={shotNumber} disabled={autoload} min="0" max="10000" style="max-width: 5em;" on:change={loadShotData} />
        </label>
    </form>
    <hr>
    <div style="overflow-y: scroll;">
        <JsonView json={shotData} />
    </div>
</nav>

<div class="main">
    <div style="column-count: 2">
        {#each images as image}
            <div class="image-container" style="display: block; break-inside: avoid;">
                <h2>{image.metadata.title}</h2>
                <img class="image" src={image.url} alt={image.metadata.title} />
                <div class="metadata">
                    <JsonView json={image.metadata} />
                </div>
            </div>
        {/each} 
    </div>
</div>