document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const suggestionsBox = document.getElementById("suggestions");

    let debounceTimer;
    let lastQuery = "";
    let controller = null; // For aborting previous fetch

    // Debounce function to limit API calls
    function debounce(func, delay) {
        return function(...args) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Fetch suggestions from backend
    const fetchSuggestions = debounce(async function() {
        const query = searchInput.value.trim();
        if (query.length < 2) {
            suggestionsBox.innerHTML = "";
            return;
        }

        // Cancel previous request
        if (controller) {
            controller.abort();
        }
        controller = new AbortController();
        const signal = controller.signal;

        lastQuery = query;

        try {
            const res = await fetch(`/search_suggestions?query=${encodeURIComponent(query)}`, { signal });
            if (!res.ok) return;
            const data = await res.json();

            // Prevent old results from overwriting newer ones
            if (query !== lastQuery) return;

            suggestionsBox.innerHTML = "";
            if (data.length === 0) {
                suggestionsBox.style.display = "none";
                return;
            }

            suggestionsBox.style.display = "block";
            data.forEach(item => {
                const option = document.createElement("a");
                option.href = `/search?query=${encodeURIComponent(item)}`;
                option.classList.add("list-group-item", "list-group-item-action");
                option.textContent = item;
                suggestionsBox.appendChild(option);
            });

        } catch (err) {
            if (err.name !== "AbortError") {
                console.error("Error fetching suggestions:", err);
            }
        }
    }, 250); // 250ms delay

    searchInput.addEventListener("input", fetchSuggestions);

    // Keep dropdown open when clicking a suggestion
    suggestionsBox.addEventListener("mousedown", function(e) {
        e.preventDefault(); // Prevent losing focus before click
    });

    // Hide when clicking outside
    document.addEventListener("click", function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = "";
            suggestionsBox.style.display = "none";
        }
    });

    