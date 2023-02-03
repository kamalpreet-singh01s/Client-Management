let gst_select = document.getElementById('gst');
let amount_by_user = document.getElementById('amount_by_user');
let final_deal_including_gst = document.getElementById('final_deal_including_gst');

//console.log(final_deal_amount)
gst_select.onchange = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
}


window.onload = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
}





amount_by_user.onchange = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
}

