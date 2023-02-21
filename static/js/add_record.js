let gst_select = document.getElementById('gst');
let amount_by_user = document.getElementById('amount_by_user');
let gst_amount = document.getElementById('gst_amount');
let total_amount_including_gst = document.getElementById('total_amount_including_gst');

//console.log(final_deal_amount)
gst_select.onchange = function () {
    gst_no = gst_select.value;



    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
}


window.onload = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
}





amount_by_user.onchange = function () {
    gst_no = gst_select.value;




    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        total_amount_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        gst_amount.value = total_amount_including_gst.value - amount_by_user.value

        if (amount_by_user.value.length == 0){
        
        gst_amount.value = '0';
        total_amount_including_gst.value = '0';

    }
    }
}





let credit = document.getElementById('credit');
let client_name_select = document.getElementById('client_name');

client_name_select.onchange = function () {
    client_name = client_name_select.value;
    fetch('/get_credit_list/' + client_name).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (client of data.credit_list) {

            credit.value = client.client_credit_amount;
            }
            console.log(optionHTML)

        });
    });
}

client_name_select.onload = function () {
    client_name = client_name_select.value;
    fetch('/get_credit_list/' + client_name).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (client of data.credit_list) {

            credit.value = client.client_credit_amount;
            }
            console.log(optionHTML)

        });
    });
}


window.onload = function () {
    client_name = client_name_select.value;
    fetch('/get_credit_list/' + client_name).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (client of data.credit_list) {

            credit.value = client.client_credit_amount;
            }
            console.log(optionHTML)

        });
    });
}