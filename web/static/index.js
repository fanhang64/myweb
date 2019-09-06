$(document).ready(function() {
	var editor = ace.edit("editor", {
        maxLines: 40,minLines: 40
	});
	editor.setAutoScrollEditorIntoView(true);
    editor.setTheme("ace/theme/tomorrow");
	editor.session.setMode("ace/mode/python");
	$(".share-btn").bind("click", function() { 
		var text = editor.getValue();
		if (!text){
			return;
		}
		console.log(text, " text====")
		$.ajax({
			url: '/share/', 
			type: 'post',
			contentType: "application/json",
			data: JSON.stringify({
				content: text
			}),
			dataType: 'json',
			success: function(res){
				console.log(res, "====")
				var res = res;
				if (res.errcode == 0){
					window.location.href = res.data;
				}else{
					alert('创建分享链接失败');
				}
			},
			fail: function(res){
				alert('创建分享链接失败');
			}
		});
	}); 
});
