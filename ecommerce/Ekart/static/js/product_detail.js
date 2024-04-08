$(document).ready(function () {
    // Initialize ezPlus for image zoom
    $('.img-big-wrap').ezPlus({
        zoomType: 'inner',
        cursor: 'crosshair',
        gallery: 'thumb',
        responsive: true
    });

    // Product image selection
    $(".thumb a").on('click', function(e) {
        e.preventDefault();
        var imageUrl = $(this).attr('href');
        $(".img-big-wrap img").attr('src', imageUrl);
    });

    // Product variant selection
    $(".item-option-select select").on('change', function() {
        var selectedOption = $(this).val();
        var optionType = $(this).attr('name');

        // Update selected variant value
        $('input[name="' + optionType + '"]').val(selectedOption);

        // Update price or perform other actions based on the selected variant
        // Add your code here
    });

    // Add to cart form submission
    $("form[action^='{% url 'add_cart' %}']").on('submit', function(e) {
        e.preventDefault();

        var formData = $(this).serialize();

        // Submit form data via AJAX
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: formData,
            success: function(response) {
                // Handle success response
                console.log('Product added to cart successfully.');
            },
            error: function(xhr, status, error) {
                // Handle error response
                console.error('Error adding product to cart:', error);
            }
        });
    });

    // Review form submission
    $("form[action^='{% url 'submit_review' %}']").on('submit', function(e) {
        e.preventDefault();

        var formData = $(this).serialize();

        // Submit form data via AJAX
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: formData,
            success: function(response) {
                // Handle success response
                console.log('Review submitted successfully.');
                // Refresh the page or update the review section
                window.location.reload();
            },
            error: function(xhr, status, error) {
                // Handle error response
                console.error('Error submitting review:', error);
            }
        });
    });
});
