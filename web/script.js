document.getElementsByName('student_name')[0].addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementsByName('student_id')[0].focus();
});

document.getElementsByName('student_id')[0].addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementsByClassName('check_button')[0].click();
});

let checkButtonClicked = false;
let clearButtonClicked = false;

const check_button_clicked = () => {
    checkButtonClicked = true;
}

const clear_button_clicked = () => {
    clearButtonClicked = true;

    if ($('.clear_button').html() == '刪除') {
        $('#data_table').DataTable().row('.selected').remove().draw(false);
    }
}

function studentNameInputOnClick() {
    let studentNameInput = document.getElementsByName("student_name")[0];
    navigator.clipboard.writeText(studentNameInput.value);
}

function studentIdInputOnClick() {
    let studentIdInput = document.getElementsByName("student_id")[0];
    navigator.clipboard.writeText(studentIdInput.value);
}

const detectSightContainer = $("#detection_sight_container");

let tableShowed = false;

async function data_button_clicked() {
    $('#data_button').attr('onclick', '');

    if (tableShowed) {
        tableShowed = false;
        await removeFadeOut(detectSightContainer.children().first(), 500);
        showCamera();
    } else {
        tableShowed = true;
        await removeFadeOut(detectSightContainer.children().first(), 500);
        showTable();
    }

    setTimeout(() => { $('#data_button').attr('onclick', 'data_button_clicked()'); }, 500);
}

function removeFadeOut(element, speed) {
    return new Promise(resolve => {
        element.fadeOut(speed);
        setTimeout(() => {
            element.remove();
            resolve();
        }, speed);
    })
}

function showTable() {
    createDOMTable();
    enhaceTable()
    tableAddOnClickListener();
}

function createDOMTable() {
    let div = document.createElement("div");
    div.className = "table_wrapper";

    let table = document.createElement("table");
    table.id = "data_table";
    table.className = "table table-striped table-bordered table-hover";
    table.style.width = "100%"

    let header = table.createTHead();
    let row = header.insertRow(0);
    row.insertCell(0).innerHTML = "姓名";
    row.insertCell(1).innerHTML = "證號";

    div.appendChild(table);
    detectSightContainer.append(div);
}

function enhaceTable() {
    $('#data_table').DataTable({
        "lengthChange": false,
        "pageLength": 17,
        language: lang
    });
}

function tableAddOnClickListener() {
    $('#data_table tbody').on('click', 'tr', function() {
        if ($(this)[0].innerText !== '目前沒有資料') {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                $('input[name="student_name"]').val("");
                $('input[name="student_id"]').val("");
            } else {
                $('#data_table').DataTable().$('tr.selected').removeClass('selected');
                $(this).addClass('selected');
                $('input[name="student_name"]').val($('#data_table').DataTable().row(this).data()[0]);
                $('input[name="student_id"]').val($('#data_table').DataTable().row(this).data()[1]);
            }
        }
    });
}