document.addEventListener("DOMContentLoaded", () => {
    const tickerInput = document.getElementById("ticker-search") || 
                        document.querySelector('input[name="ticker"]');
    if (!tickerInput) return;

    const dropdown = document.createElement("ul");
    dropdown.style.cssText = "position:absolute;background:white;border:1px solid #ccc;list-style:none;padding:0;margin:0;z-index:999;min-width:300px;";
    tickerInput.parentNode.style.position = "relative";
    tickerInput.parentNode.appendChild(dropdown);

    let timeout;
    tickerInput.addEventListener("input", () => {
        clearTimeout(timeout);
        const q = tickerInput.value.trim();
        if (q.length < 2) { dropdown.innerHTML = ""; return; }
        timeout = setTimeout(async () => {
            const res = await fetch(`/api/search-ticker?q=${q}`);
            const items = await res.json();
            dropdown.innerHTML = "";
            items.forEach(item => {
                const li = document.createElement("li");
                li.textContent = `${item.symbol} — ${item.name}`;
                li.style.cssText = "padding:8px 12px;cursor:pointer;border-bottom:1px solid #eee;";
                li.addEventListener("mouseenter", () => li.style.background = "#f0f0f0");
                li.addEventListener("mouseleave", () => li.style.background = "white");
                li.addEventListener("click", () => {
                    tickerInput.value = item.symbol;
                    const nameField = document.querySelector('input[name="name"]');
                    if (nameField) nameField.value = item.name;
                    dropdown.innerHTML = "";
                });
                dropdown.appendChild(li);
            });
        }, 300);
    });

    document.addEventListener("click", (e) => {
        if (!tickerInput.contains(e.target)) dropdown.innerHTML = "";
    });
});
