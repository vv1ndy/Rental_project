mapboxgl.accessToken = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g";
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [105.854444, 21.0285], // Mặc định: Hà Nội, Việt Nam
    zoom: 12
});

async function loadListings(longitude, latitude) {
    try {
        let url = '/get_listings';
        if (longitude && latitude) {
            url += `?longitude=${longitude}&latitude=${latitude}`;
        }

        const response = await fetch(url);
        const listings = await response.json();
        const listingContainer = document.getElementById('listing-container');
        listingContainer.innerHTML = '';

        listings.forEach(listing => {
            const div = document.createElement('div');
            div.classList.add('listing-item');
            div.innerHTML = `
                <h3>${listing.title}</h3>
                <p><strong>Địa chỉ:</strong> ${listing.address}</p>
                <p><strong>Giá thuê:</strong> ${listing.price} VNĐ</p>
                <img src="${listing.image}" alt="Hình ảnh nhà trọ">
            `;
            listingContainer.appendChild(div);

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

// Search form handler
document.getElementById('search-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const address = document.getElementById('search-address').value;

    try {
        const geocodeResponse = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(address)}.json?access_token=${mapboxgl.accessToken}`);
        const geocodeData = await geocodeResponse.json();
        
        if (geocodeData.features.length === 0) {
            alert('Không tìm thấy địa chỉ!');
            return;
        }

        const [longitude, latitude] = geocodeData.features[0].center;

        // Fly to the searched location
        map.flyTo({ center: [longitude, latitude], zoom: 15 });

        // Load listings near the searched location
        loadListings(longitude, latitude);
    } catch (error) {
        console.error('Lỗi khi tìm kiếm địa chỉ:', error);
    }
});