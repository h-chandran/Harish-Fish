async function fetchHealth() {
    const output = document.getElementById("output");
    output.textContent = "Checking backend health...";

    try {
        const response = await fetch("/health");
        const data = await response.json();
        output.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        output.textContent = `Request failed: ${error}`;
    }
}

async function hitPlaceholder(url, method = "POST") {
    const output = document.getElementById("output");
    output.textContent = `Calling ${url}...`;

    try {
        const response = await fetch(url, { method });
        const data = await response.json();
        output.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        output.textContent = `Request failed: ${error}`;
    }
}
