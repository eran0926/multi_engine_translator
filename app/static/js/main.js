// event listener
$('#swich-lan-btn').on('click', switch_lan);
$('#tranSubmitBtn').on('click', submitTran)
// $('#in_textarea').on('input', in_textarea_change);
let queued = false
document.getElementById("in_textarea").addEventListener('input', () => {
    if (!queued) {
        queued = true
        requestIdleCallback(() => {
            in_textarea_change(document.getElementById("in_textarea").value)
            queued = false
        })
    }
})


function switch_lan() {
    let ori_lan_select = $('#ori_lan_select');
    let tar_lan_select = $('#tar_lan_select');
    let ori_tar_lan = tar_lan_select.val();
    tar_lan_select.val(ori_lan_select.val());
    ori_lan_select.val(ori_tar_lan);
}

function in_textarea_change(text) {
    // var in_textarea = $('#in_textarea');
    // var text = in_textarea.val();
    predicts = get_predicts(text);
    change_predict(predicts)
}

function get_predicts(text) {
    let re = new Array();
    re.length = 0;
    // for (var i = 0; i < 10; i++) {
    //     re[i] = { "word": "" }
    // }
    $.ajax({
        url: '/translator/get_predicts?q=' + text,
        method: 'GET',
        async: false,
        // dataType: "json",
        success: function (res) {
            // console.log('success', typeof (res))
            res.forEach(function (element, index) {
                // console.log(typeof (index))
                re[index] = { 'word': element['word'] }
                // re.push({ 'word': element['word'] });
                // console.log(re.length)
            });
            return;
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

function change_predict(predict_arr) {
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
}

function submitTran() {
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
    if (text != '') {
        var data = [{
            'from': ori_lan,
            'to': tar_lag,
            'text': text,
            'engines': engines
        }]
        var url = '/translator/translator'
        re = postJsonData(url, data)
        console.log(re)
        changeTranResult(re)

    }
}

function postJsonData(url, data) {
    var re;
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json;charset=utf-8",
        async: false,
        success: function (res) {
            // console.log('ajax result:')
            // console.log(res.stringify)
            re = res
        },
        error: function (res) {
            console.log('ajax error:')
            console.log(res)
            re = 'error'
        }
    });
    return re
}

function changeTranResult(data) {
    resultTable = $('#resultTable').find('tbody')
    resultTable.html('')
    for (let dataIndex = 0; dataIndex < data.length; dataIndex++) {
        Object.entries(data[dataIndex]['translations']).forEach(([engine, tranData]) => {
            if (engine == 'cambridge') {
                console.log(tranData)
                for (let index = 0; index < tranData.length; index++) {
                    html = '<tr>'
                    if (index == 0) {
                        html += '<td rowspan="' + tranData.length + '">' + '劍橋' + '</td>\n'
                    }
                    html += '<td>' + tranData[index]['pos'] + '</td>\n'
                    // html += '<td>' + tranData[index]['from'] + '</td>\n'
                    translations = tranData[index]['to']
                    html += '<td><ul>'
                    for (let i = 0; i < translations.length; i++) {
                        html += '<li>' + translations[i] + '</li>'
                    }
                    html += '</ul></td>\n'
                    html += '</tr>'
                    resultTable.html(resultTable.html() + html)

                }
            }
            else if (engine == 'azure') {
                html = '<tr>'
                html += '<td>' + '微軟' + '</td>'
                html += '<td>' + 'none' + '</td>\n'
                html += '<td>' + tranData + '</td>\n'
                html += '</tr>'
                resultTable.html(resultTable.html() + html)
            }
            else if (engine == 'google') {
                html = '<tr>'
                html += '<td>' + 'Google' + '</td>'
                html += '<td>' + 'none' + '</td>\n'
                html += '<td>' + tranData + '</td>\n'
                html += '</tr>'
                resultTable.html(resultTable.html() + html)
            }
        })
    }
}