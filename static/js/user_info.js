$(function(){
  $('#id_icon_image').change(function(e){
    //ファイルオブジェクトを取得する
    var file = e.target.files[0];
    var reader = new FileReader();

    //画像でない場合は処理終了
    if(file.type.indexOf("image") < 0){
      alert("画像ファイルを指定してください。");
      return false;
    }

    //アップロードした画像を設定する
    reader.onload = (function(file){
      return function(e){
        $("#preview").attr("src", e.target.result);
        $("#preview").attr("title", file.name);
      };
    })(file);
    reader.readAsDataURL(file);

  });
});

function changeDisplay(onMode, offMode){
  document.getElementById(onMode).style.display = "inline";
  document.getElementById(offMode).style.display = "none";
}
