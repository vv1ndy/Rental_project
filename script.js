mapboxgl.accessToken = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g"  ;
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [105.854444, 21.0285], // Mặc định: Hà Nội, Việt Nam
    zoom: 12
});

async function loadListings() {
    try {
        const response = await fetch('/get_listings');
        const listings = await response.json();
        const listingContainer = document.getElementById('listing-container');
        listingContainer.innerHTML = '';

        listings.forEach(listing => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${listing.title}</strong> - ${listing.address} - ${listing.price} VND`;
            listingContainer.appendChild(li);

            // Add marker to the map
            new mapboxgl.Marker()
                .setLngLat([parseFloat(listing.longitude), parseFloat(listing.latitude)])
                .setPopup(new mapboxgl.Popup().setHTML(`<h3>${listing.title}</h3><p>${listing.address}</p>`))
                .addTo(map);
        });
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu nhà trọ:', error);
    }
}

// Fetch data and populate map when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadListings();
});

// Submit form handler
document.getElementById('listing-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const address = document.getElementById('address').value;
    const price = document.getElementById('price').value;
    
    try {
        const geocodeResponse = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(address)}.json?access_token=${mapboxgl.accessToken}`);
        const geocodeData = await geocodeResponse.json();
        
        if (geocodeData.features.length === 0) {
            alert('Không tìm thấy địa chỉ!');
            return;
        }

        const [longitude, latitude] = geocodeData.features[0].center;

        const response = await fetch('/add_listing', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title, address, price, latitude, longitude })
        });
        
        const data = await response.json();
        if (data.success) {
            alert('Thêm nhà trọ thành công!');
            this.reset();
            location.reload();
        } else {
            alert('Lỗi khi thêm nhà trọ!');
        }
    } catch (error) {
        console.error('Lỗi khi xác định vị trí:', error);
    }
});
