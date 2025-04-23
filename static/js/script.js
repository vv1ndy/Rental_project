mapboxgl.accessToken = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g";
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [105.854444, 21.0285], // Mặc định: Hà Nội, Việt Nam
    zoom: 12
});

let allListings = []; // Lưu trữ tất cả nhà trọ

// Function to load listings from the server
async function loadListings() {
    try {
        const response = await fetch('/get_listings');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        allListings = await response.json(); // Cập nhật dữ liệu
        displayListings(allListings); // Hiển thị dữ liệu ban đầu
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu nhà trọ:', error);
    }
}

// Function to display listings
function displayListings(listings) {
    const listingContainer = document.getElementById('listing-container');
    listingContainer.innerHTML = ''; // Xóa nội dung cũ

    listings.forEach(listing => {
        const div = document.createElement('div');
        div.classList.add('listing-item');
        div.innerHTML = `
            <h3>${listing.title}</h3>
            <p><strong>Họ và tên chủ trọ:</strong> ${listing.name}</p>
            <p><strong>Số điện thoại:</strong> ${listing.phonenumber}</p>
            <p><strong>Địa chỉ:</strong> ${listing.address}</p>
            <p><strong>Giá thuê:</strong> ${listing.price} VNĐ</p>
            <img src="${listing.image_url}" alt="Hình ảnh nhà trọ">
        `;
        listingContainer.appendChild(div);

        // Thêm marker vào bản đồ
        new mapboxgl.Marker()
            .setLngLat([parseFloat(listing.longitude), parseFloat(listing.latitude)])
            .setPopup(new mapboxgl.Popup().setHTML(`<h3>${listing.title}</h3><p>${listing.address}</p>`))
            .addTo(map);
    });
}

// Function to filter listings by area and price
function filterListings(listings, area, priceRange) {
    return listings.filter(listing => {
        // Lọc theo khu vực
        const areaMatch = !area || listing.address.includes(area);

        // Lọc theo khoảng giá
        let priceMatch = true;
        if (priceRange) {
            const [min, max] = priceRange.split('-');
            const price = parseFloat(listing.price);

            if (max === "") {
                priceMatch = price >= parseFloat(min);
            } else if (min === "") {
                priceMatch = price <= parseFloat(max);
            } else {
                priceMatch = price >= parseFloat(min) && price <= parseFloat(max);
            }
        }

        return areaMatch && priceMatch;
    });
}

// Event listener for search form
document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn form gửi request mặc định

    const area = document.getElementById('area-filter').value;
    const priceRange = document.getElementById('price-filter').value;

    // Lọc theo khu vực và khoảng giá
    const filteredListings = filterListings(allListings, area, priceRange);

    displayListings(filteredListings); // Hiển thị kết quả đã lọc
});

// Fetch data and populate map when page loads
document.addEventListener('DOMContentLoaded', loadListings);
/////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Xử lý form đăng nhà trọ
document.getElementById('add-listing-form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Ngăn form gửi request mặc định

    const title = document.getElementById('title').value;
    const name = document.getElementById('name').value;
    const phonenumber = document.getElementById('phonenumber').value;
    const address = document.getElementById('address').value;
    const price = document.getElementById('price').value;
    const image = document.getElementById('image').value;
    const description = document.getElementById('description').value;

    try {
        // Geocode địa chỉ để lấy tọa độ
        const geocodeResponse = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(address)}.json?access_token=${mapboxgl.accessToken}`);
        const geocodeData = await geocodeResponse.json();

        if (geocodeData.features.length === 0) {
            alert('Không tìm thấy địa chỉ!');
            return;
        }

        const [longitude, latitude] = geocodeData.features[0].center;

        // Gửi dữ liệu lên server
        const response = await fetch('/add_listing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                name,
                phonenumber,
                address,
                price,
                image_url: image,
                description,
                longitude,
                latitude
            }),
        });

        const data = await response.json();
        if (data.success) {
            alert('Đăng nhà trọ thành công!');
            window.location.href = 'index.html'; // Chuyển về trang chủ
        } else {
            alert('Lỗi khi đăng nhà trọ!');
        }
    } catch (error) {
        console.error('Lỗi khi đăng nhà trọ:', error);
        alert('Đã xảy ra lỗi, vui lòng thử lại!');
    }
});