<title>ImfitTre</title>

<script>
// @ts-nocheck

    import { JsonView } from '@zerodevx/svelte-json-view';
    import { onMount } from 'svelte';

    async function poll_for_new_data() {
        if (autoload) {
            loadShotData();
        }
        setTimeout(poll_for_new_data, 2000);
    }

    let autoload;
    let date;
    let shotNumber;

    let minOD = -0.1;
    let maxOD = 1.0;
    
    $: shotId = date + '_' + shotNumber;

    let shotData;

    onMount(() => {
        autoload = true;
        loadShotData();
        poll_for_new_data();
    });

    async function loadShotData(id="") {
        let url;
        if (id === "") {
            url = 'http://192.168.107.24:8000/shot?require_image=True';
        } else {
            url = 'http://192.168.107.24:8000/shot?shot_id=' + id;
        }
        try {
            shotData = await fetch(url).then(res => res.json());
        } catch (error) {
            shotData = {
                error: error.toString(),
                url: url
            };
        }

        if (id === "") {
            date = shotData._id.substring(0, 10).replaceAll('_', '-');
            shotNumber = shotData._id.substring(11);
        }
    }

    function autoOD() {
        minOD = 1000;
        maxOD = -1000;
        for (const image of images) {
            const result = image.metadata.fit.result;
            const min_fit_OD = result.params.offset - 0.1
            const max_fit_OD = result.params.offset + result.params.A + 0.1
            minOD = Math.min(minOD, min_fit_OD);
            maxOD = Math.max(maxOD, max_fit_OD);
            console.log(minOD, maxOD);
        }
    }

    // when date or shotNumber changes, load new shot data if autoload is disabled
    $: if ((!autoload)) {
        if (date !== undefined && shotNumber !== undefined) {
            loadShotData(shotId);
        }
    } else {
        loadShotData()
    }
    
    // load new images reactive to shotData
    let images = []
    $: if (shotData !== undefined) {
        images = [];
        const fits = shotData.fit;
        for (const fit in fits) {
            let N = 0;
            try {
                N = Math.round(fits[fit].result.derived.N);
            } catch (error) {
                console.log(error);
                continue;
            }
            const element = {
            id: fit,
            url: `http://192.168.107.24:8000/frame?shot_id=${shotData._id}&image=${fit}&min_val=${minOD}&max_val=${maxOD}&show_fit=True&width=300`,
            title: fit,
            metadata: {
                N: N,
                fit: fits[fit]
            }
        };
        images.push(element);
        }
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
        background-repeat: no-repeat;
        background-size: contain;
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
            <input type="checkbox" bind:checked={autoload}/>
        </label>
        <label>
            Date:
            <input type="date" bind:value={date} disabled={autoload}/>
        </label>
        <label>
            Shot:
            <input type="number" bind:value={shotNumber} disabled={autoload} min="0" max="10000" style="max-width: 5em;"/>
        </label>
    </form>
    <br>
    <div style="display: flex; flex-direction: row; align-items:center; justify-content: left; flex-wrap: wrap;">
        <label>
            Min OD:
            <input type="number" min="-0.3" max={maxOD} bind:value={minOD} step="0.1" style="max-width: 5em; margin-right: 10px;">
        </label>
        <label>
            Max OD:
            <input type="number" min={minOD} max="3.0" bind:value={maxOD} step="0.1" style="max-width: 5em; margin-right: 10px;">
        </label>
        <button on:click={autoOD}>Auto OD</button>
    </div>
    <hr>
    <div style="overflow-y: scroll;">
        <JsonView json={shotData} depth=1/>
    </div>
</nav>

<div class="main">
    <div style="column-count: 2; column-width:400px; column-gap: 20px;">
        {#each images as image}
            <div class="image-container" style="display: block; break-inside: avoid;">
                <h2>{image.title}</h2>
                <canvas class="image" style="background-image: url('{image.url}')" id={image.id}></canvas>
                <div class="metadata">
                    <JsonView json={image.metadata} depth=1/>
                </div>
            </div>
        {/each} 
    </div>
</div>