                    status_name = document.getElementById('status')
if (status_name.innerHTML == "Approved" || status_name.innerHTML == "Cancelled"){
console.log('status_name')
    approve_button = document.getElementById('approve_button');
    approve_button.parentNode.removeChild(approve_button);
    cancel_button = document.getElementById('cancel_button');
    cancel_button.parentNode.removeChild(cancel_button);
    }




if (status_name.innerHTML == "Approved"){
    status_name.style.color = "green";
    status_name.style.fontWeight = "bolder";
}

if (status_name.innerHTML == "Cancelled"){
    status_name.style.color = "red";
    status_name.style.fontWeight = "bolder";
}
if (status_name.innerHTML == "Draft"){
    status_name.style.color = "#5F5DFF";
    status_name.style.fontWeight = "bolder";
}
