//Code from the django-chunked-upload example

let md5 = "";
const csrf = $("input[name='csrfmiddlewaretoken']")[0].value;
let form_data = [{"name": "csrfmiddlewaretoken", "value": csrf}];
const chunkSize = 50000000; //50 MB

function calculate_md5(file, chunk_size) {
    let slice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice;
    let chunks = Math.ceil(file.size / chunk_size);
    let current_chunk = 0;
    let spark = new SparkMD5.ArrayBuffer();

    function onload(e) {
        spark.append(e.target.result);  // append chunk
        current_chunk++;
        if (current_chunk < chunks) {
            read_next_chunk();
        } else {
            md5 = spark.end();
        }
    }
    function read_next_chunk() {
        const reader = new FileReader();
        reader.onload = onload;
        const start = current_chunk * chunk_size;
        const end = Math.min(start + chunk_size, file.size);
        reader.readAsArrayBuffer(slice.call(file, start, end));
    }
    read_next_chunk();
}
$("#id_file").fileupload({
    url: upload_url,
    dataType: "json",
    maxChunkSize: chunkSize,
    dropZone: null,
    formData: form_data,

    add: function(e, data) { // Called when a file is selected
        $("#file-upload-name").html(data.files[0].name);
        $("#file-upload-size").html(data.files[0].size);
        $("#file_upload_btn").off('click').on('click', function () {
            calculate_md5(data.files[0], chunkSize);
            data.submit();
        });
    },
    chunkdone: function (e, data) { // Called after uploading each chunk
        if (form_data.length < 2) {
            form_data.push(
                {"name": "upload_id", "value": data.result.upload_id}
            );
        }
        let progress = parseInt(data.loaded / data.total * 100.0, 10);
        $("#file-upload-progress").html(progress + "%");
    },
    done: function (e, data) { // Called when the file has completely uploaded
        let formData = $("#file-upload-form").serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});
        formData['upload_id'] = data.result.upload_id;
        formData['md5'] = md5;

        $.ajax({
            type: "POST",
            url: upload_complete_url,
            data: formData,
            dataType: "json",
            success: function() {
                window.location.reload(true)
            }
        });
    },
});