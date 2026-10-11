document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. MONITORING MAP INITIALIZATION
    // ==========================================
    if (document.getElementById('monitoringMap')) {
        // Initialize map centered on Delhi
        const map = L.map('monitoringMap').setView([28.7041, 77.1025], 11);

        // Load OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Fetch reports from the existing backend route
        fetch('http://127.0.0.1:5000/api/reports')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.reports) {
                    // Loop through reports and add pins
                    data.reports.forEach(report => {
                        if (report.latitude && report.longitude) {
                            const marker = L.marker([report.latitude, report.longitude]).addTo(map);
                            
                            // Color code severity
                            let severityColor = 'green';
                            if (report.severity === 'High') severityColor = 'red';
                            if (report.severity === 'Medium') severityColor = 'orange';

                            // Popup content
                            const popupContent = `
                                <div style="font-family: inherit;">
                                    <strong style="font-size: 16px; color: #0f1c2e;">${report.location_name}</strong><br>
                                    <span style="color: ${severityColor}; font-weight: bold;">
                                        ${report.severity} Severity
                                    </span><br>
                                    <p style="margin: 8px 0 0 0; font-size: 14px; color: #333;">${report.description}</p>
                                </div>
                            `;
                            marker.bindPopup(popupContent);
                        }
                    });
                }
            })
            .catch(error => console.error('Error fetching map pins:', error));
    }


    // ==========================================
    // 2. REPORT FORM SUBMISSION & AI ANALYSIS
    // ==========================================
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Gather form data
            const location_name = document.getElementById('location_name').value;
            const description = document.getElementById('description').value;
            const severity = document.getElementById('severity').value;
            const latitude = document.getElementById('latitude').value;
            const longitude = document.getElementById('longitude').value;
            const imageFile = document.getElementById('image').files[0];

            // UI Elements for AI result
            const aiMessage = document.getElementById('aiMessage');
            const aiResult = document.getElementById('aiResult');
            const aiOutputImage = document.getElementById('aiOutputImage');
            
            try {
                // Step A: Save text data to PostgreSQL
                const dbResponse = await fetch('http://127.0.0.1:5000/api/reports', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        location_name: location_name,
                        description: description,
                        severity: severity,
                        latitude: latitude ? parseFloat(latitude) : null,
                        longitude: longitude ? parseFloat(longitude) : null
                    })
                });
                
                const dbData = await dbResponse.json();
                if (!dbData.success) {
                    alert("Error saving report: " + dbData.message);
                    return;
                }
                
                alert("Report saved to database successfully!");

                // Step B: Send image to YOLOv8 AI Model
                if (imageFile) {
                    // Show loading UI
                    aiResult.style.display = 'block';
                    aiMessage.textContent = 'Analyzing image with AI... please wait.';
                    aiOutputImage.style.display = 'none';

                    const formData = new FormData();
                    formData.append('image', imageFile);

                    const aiResponse = await fetch('http://127.0.0.1:5000/api/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    const aiData = await aiResponse.json();

                    if (aiData.ai_detection && aiData.ai_detection.success) {
                        aiMessage.textContent = `Analysis Complete: Detected ${aiData.ai_detection.detections.length} objects.`;
                        aiOutputImage.src = aiData.ai_detection.output_image_url;
                        aiOutputImage.style.display = 'block';
                        
                        // Automatically refresh the map to show the new pin!
                        setTimeout(() => location.reload(), 3000); 
                    } else {
                        aiMessage.textContent = 'AI Analysis failed or found nothing.';
                    }
                } else {
                    // If no image, just reload to update the map
                    location.reload();
                }

            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred during submission.");
            }
        });
    }
});