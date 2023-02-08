let bill_no_select = document.getElementById('bill_no');
let client_name = document.getElementById('client_name');

bill_no_select.onload = function () {
    bill_no = bill_no_select.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
}

bill_no_select.onchange = function () {
    bill_no = bill_no_select.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
}

window.onload = function () {
    bill_no = bill_no_select.value;
    client = client_name.value;
    fetch('/get_client_list/' + bill_no).then(function (response) {
        response.json().then(function (data) {
            console.log(data)
            optionHTML = '';
            for (let client of data.client_list) {
                optionHTML += '<option value="' + client.client_id + '">' + client.client_name + '</option>'
            }
            client_name.innerHTML = optionHTML;
        });
    });
    }


