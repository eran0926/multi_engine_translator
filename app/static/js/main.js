// event listener
$('#swich-lan-btn').on('click', switch_lan);
$('#tranSubmitBtn').on('click', submitTran)
// $('#in_textarea').on('input', in_textarea_change);
let queued = false
let timer
let old_input = ''
const rootUrl = ''
document.getElementById("in_textarea").addEventListener('input', () => {
    old_input = document.getElementById("in_textarea").value
    clearTimeout(timer);
    requestIdleCallback(() => {
        timer = setTimeout(() => {
            if (document.getElementById("in_textarea").value == old_input) {
                if (!queued) {
                    queued = true
                    setTimeout(function () {

                        console.log("catching predict")
                        in_textarea_change()
                        queued = false

                    }, 500);
                }
            }
        }, 100);
    })
})


function switch_lan() {
    let ori_lan_select = $('#ori_lan_select');
    let tar_lan_select = $('#tar_lan_select');
    let ori_tar_lan = tar_lan_select.val();
    tar_lan_select.val(ori_lan_select.val());
    ori_lan_select.val(ori_tar_lan);
}

function in_textarea_change() {
    // var in_textarea = $('#in_textarea');
    // var text = in_textarea.val();
    text = document.getElementById("in_textarea").value
    predicts = get_predicts(text);
}

function get_predicts(text) {
    let re = new Array();
    re.length = 0;
    // for (var i = 0; i < 10; i++) {
    //     re[i] = { "word": "" }
    // }
    $.ajax({
        url: rootUrl + '/get_predicts?q=' + text,
        method: 'GET',
        // async: false,
        // dataType: "json",
        success: function (res) {
            // console.log('success', typeof (res))
            res.forEach(function (element, index) {
                // console.log(typeof (index))
                re[index] = { 'word': element['word'] }
                // re.push({ 'word': element['word'] });
                // console.log(re.length)
            });
            update_predict(re)

        },
        error: function (res) {
            console.log("Error:");
            console.log(res);
        }
    });
    // console.log(re.toString())
    // console.log(re[0])
    // console.log(re.length)
    return re;
}

function update_predict(predict_arr) {
    predicts = predict_arr
    console.log(predicts)
    // console.log(typeof (predicts))
    max_predict = 5;
    predict_num = Math.min(max_predict, predicts.length)
    table = $('#predict_table').find('tbody')
    table.html('')
    for (var i = 0; i < predict_num; i++) {
        text = predicts[i]['word'];
        table.html(table.html() + '<tr onclick="use_predict(\'' + text + '\');"><td>' + text + '</td></tr>\n')
        // console.log(text, "--", table.html())
    }


    // $('#predict_table tr:not(:first)').each(function (index) {
    //     console.log("index:", index)
    //     console.log(predicts[index])
    //     text = predicts[index]['word'];
    //     // text = predicts[index];
    //     $(this).attr('onClick', 'javascript: use_predict(' + text + ');');
    //     $(this, 'td').text(text);

    // });
}

function use_predict(text) {
    var in_textarea = $('#in_textarea');
    in_textarea.val(text)
}

// document.getElementById("in_textarea").addEventListener("input", in_textarea_change);


function restTextarea() {
    $('#in_textarea').val('')
    $('#in_textarea').focus()
}

function submitTran() {

    postData = getPostData()

    if (!getPostData) {
        return
    }

    $('#tranSubmitBtn').prop('disabled', true)
    document.getElementById("result_div").setAttribute("style", "display: none;")
    document.getElementById("tran_loader").setAttribute("style", "display: block;")


    var url = rootUrl + '/get_translation_async'
    postJsonData(url, postData)





}

function getPostData() {
    var ori_lan = $('#ori_lan_select').val()
    var tar_lag = $('#tar_lan_select').val()
    var text = $('#in_textarea').val()
    var engines = new Array;
    $('#engineContrl input:checkbox').each(function (index) {
        // console.log($(this))
        // console.log($(this).is(":checked"))
        if ($(this).is(":checked")) {
            engines.push($(this).val())
        }
    })

    if (text == '') {
        return null
    }

    return [{
        'from': ori_lan,
        'to': tar_lag,
        'text': text,
        'engines': engines
    }]
}


function postJsonData(url, data) {
    const start = Date.now();

    resultTable = $('#resultTable').find('tbody')
    resultTable.html('')
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        }
    })
        .then((response) => {
            r = response.json()
            console.log(r)
            return r
        })
        .then(response => {
            console.log('Success:', response);
            UpdateTranResult(response)
            const end = Date.now();
            console.log(`Execution time: ${end - start} ms`);
        })
        .catch(error => {
            console.error('Error:', error);
            resultTable = $('#resultTable').find('tbody')
            resultTable.append('<tr><td colspan="3">翻譯失敗</td></tr>')
        })
        .finally(() => {
            document.getElementById("result_div").setAttribute("style", "display: block;")
            document.getElementById("tran_loader").setAttribute("style", "display: none;")
            setTimeout(function () {
                $('#tranSubmitBtn').prop('disabled', false)
            }, 500);
        })

}

function UpdateTranResult(result) {

    data = result['data']['translations'][0]

    for (let tran of data) {
        if (tran['code'] != 200) {
            continue
        }

        if (tran['engine'] == 'cambridge') {
            for (let tranData of tran['translations']) {
                engineTd = document.createElement('td')
                engineTd.innerText = '劍橋'

                tr = document.createElement('tr')
                tr.appendChild(engineTd)

                posTd = document.createElement('td')
                posTd.innerText = tranData['pos']
                tr.appendChild(posTd)
                ul = document.createElement('ul')
                for (let translation of tranData['trans']) {
                    li = document.createElement('li')
                    li.innerText = translation
                    ul.appendChild(li)
                }

                tranTd = document.createElement('td')
                tranTd.appendChild(ul)
                tr.appendChild(tranTd)

                resultTable.append(tr)
            }
        }
        if (tran['engine'] == 'azure') {
            tr = document.createElement('tr')
            engineTd = document.createElement('td')
            engineTd.innerText = '微軟'
            tr.appendChild(engineTd)
            posTd = document.createElement('td')
            posTd.innerText = 'none'
            tr.appendChild(posTd)
            tranTd = document.createElement('td')
            tranTd.innerText = tran['tran']
            tr.appendChild(tranTd)
            resultTable.append(tr)
        }
        if (tran['engine'] == 'google') {
            tr = document.createElement('tr')
            engineTd = document.createElement('td')
            engineTd.innerText = 'Google'
            tr.appendChild(engineTd)
            posTd = document.createElement('td')
            posTd.innerText = 'none'
            tr.appendChild(posTd)
            tranTd = document.createElement('td')
            tranTd.innerText = tran['tran']
            tr.appendChild(tranTd)
            resultTable.append(tr)
        }
    }
}
