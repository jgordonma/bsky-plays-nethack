document.addEventListener('DOMContentLoaded', function() {
    const commandForm = document.getElementById('commandForm');
    const commandInput = document.getElementById('commandInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const gameImage = document.getElementById('gameImage');
    const screenText = document.getElementById('screenText');
    const responseData = document.getElementById('responseData');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const historyItems = document.getElementById('historyItems');
    
    // Command history
    const commandHistory = [];
    
    commandForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const command = commandInput.value.trim();
        if (command) {
            // Add to history
            addToHistory(command);
            // Send command
            fetchCommand(command);
            // Clear input
            commandInput.value = '';
        }
    });
    
    function fetchCommand(command) {
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        resultsContainer.style.display = 'none';
        
        // Fetch from API
        fetch(`/api/command?command=${encodeURIComponent(command)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                resultsContainer.style.display = 'block';
                
                // Display the image
                gameImage.src = `data:image/png;base64,${data.img_base64}`;
                
                // Display the screen text
                screenText.textContent = data.screen;
                
                // Format and display the response data
                formatResponseData(data);
            })
            .catch(error => {
                console.error('Error:', error);
                loadingIndicator.style.display = 'none';
                alert('Error fetching data: ' + error.message);
            });
    }
    
    function formatResponseData(data) {
        // Create a copy of the data to avoid modifying the original
        const displayData = {...data};
        
        // Replace the base64 image data with a placeholder
        displayData.img_base64 = '[Base64 image data]';
        
        // Format the observation data if it exists
        if (displayData.obsv) {
            // Format the formatted output
            let formattedOutput = '';
            
            // Add message if it exists
            if (displayData.obsv.text_message) {
                formattedOutput += `<div class="message-section">
                    <h4>Message</h4>
                    <div class="message">${escapeHtml(displayData.obsv.text_message)}</div>
                </div>`;
            }
            
            // Format player stats
            if (displayData.obsv.text_blstats) {
                formattedOutput += `<div class="stats-section">
                    <h4>Player Stats</h4>
                    <div class="stats-grid">
                        ${formatPlayerStats(displayData.obsv.text_blstats)}
                    </div>
                </div>`;
            }
            
            // Format inventory
            if (displayData.obsv.text_inventory) {
                formattedOutput += `<div class="inventory-section">
                    <h4>Inventory</h4>
                    <div class="inventory-list">
                        ${formatInventory(displayData.obsv.text_inventory)}
                    </div>
                </div>`;
            }
            
            // Format environment
            if (displayData.obsv.text_glyphs) {
                formattedOutput += `<div class="environment-section">
                    <h4>Environment</h4>
                    <ul class="glyphs-list">
                        ${formatEnvironment(displayData.obsv.text_glyphs)}
                    </ul>
                </div>`;
            }
            
            // Format cursor (what you're looking at)
            if (displayData.obsv.text_cursor) {
                formattedOutput += `<div class="cursor-section">
                    <h4>Looking At</h4>
                    <div class="cursor">${escapeHtml(displayData.obsv.text_cursor)}</div>
                </div>`;
            }
            
            // Format game status
            formattedOutput += `<div class="game-status-section">
                <h4>Game Status</h4>
                <div class="status-grid">
                    <div class="status-item">Reward: ${displayData.reward}</div>
                    <div class="status-item">Done: ${displayData.done}</div>
                    ${displayData.info ? `<div class="status-item">End Status: ${displayData.info.end_status}</div>
                    <div class="status-item">Ascended: ${displayData.info.is_ascended}</div>` : ''}
                </div>
            </div>`;
            
            // Set the formatted output
            responseData.innerHTML = formattedOutput;
        } else {
            // If no observation data, just show the raw JSON
            responseData.textContent = JSON.stringify(displayData, null, 2);
        }
    }
    
    function formatPlayerStats(statsText) {
        // Split the stats text into lines
        const lines = statsText.split('\n');
        let statsHtml = '';
        
        // Process each line
        lines.forEach(line => {
            if (line.trim()) {
                const [key, value] = line.split(':').map(s => s.trim());
                statsHtml += `<div class="stat-item"><strong>${escapeHtml(key)}:</strong> ${escapeHtml(value)}</div>`;
            }
        });
        
        return statsHtml;
    }
    
    function formatInventory(inventoryText) {
        // Split the inventory text into lines
        const lines = inventoryText.split('\n');
        let inventoryHtml = '';
        
        // Process each line
        lines.forEach(line => {
            if (line.trim()) {
                inventoryHtml += `<div class="inventory-item">${escapeHtml(line)}</div>`;
            }
        });
        
        return inventoryHtml || '<div class="empty-inventory">No items in inventory</div>';
    }
    
    function formatEnvironment(glyphsText) {
        // Split the glyphs text into lines
        const lines = glyphsText.split('\n');
        let glyphsHtml = '';
        
        // Process each line
        lines.forEach(line => {
            if (line.trim()) {
                glyphsHtml += `<li>${escapeHtml(line)}</li>`;
            }
        });
        
        return glyphsHtml;
    }
    
    function addToHistory(command) {
        // Add to the beginning of the array
        commandHistory.unshift(command);
        
        // Keep only the last 10 commands
        if (commandHistory.length > 10) {
            commandHistory.pop();
        }
        
        // Update the UI
        updateHistoryUI();
    }
    
    function updateHistoryUI() {
        historyItems.innerHTML = '';
        commandHistory.forEach(cmd => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.textContent = cmd;
            item.addEventListener('click', function() {
                commandInput.value = cmd;
            });
            historyItems.appendChild(item);
        });
    }
    
    // Helper function to escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
