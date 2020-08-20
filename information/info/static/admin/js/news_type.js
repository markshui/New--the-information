function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    var $a = $('.edit');
    var $add = $('.addtype');
    var $pop = $('.pop_con');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');
    var $input = $('.input_txt3');
    var sHandler = 'edit';
    var sId = 0;

    // 编辑分类
    $a.click(function(){
        sHandler = 'edit';
        sId = $(this).parent().siblings().eq(0).html(); // 获取要修改分类的id
        $pop.find('h3').html('修改分类');
        $pop.find('.input_txt3').val($(this).parent().prev().html());  // 获取被点击的a标签的父元素即td，它的前一个元素的html值
        $pop.show();
    });

    // 新增分类
    $add.click(function(){
        sHandler = 'add';
        $pop.find('h3').html('新增分类');
        $input.val('');
        $pop.show();
    });

    // 取消操作
    $cancel.click(function(){
        $pop.hide();
        $error.hide();
    });

    // 每当编辑分类时，隐藏错误提示
    $input.click(function(){
        $error.hide();
    });

    // 提交数据
    $confirm.click(function(){

        var params = {};
        if(sHandler=='edit')
        {
            // 编辑分类
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "id": sId,
                "name": sVal,
            };
        }
        else
        {   // 新增分类
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "name": sVal,
            }
        }

        // TODO 发起修改分类请求
        $.ajax({
            url: "/admin/add_type",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (res) {
                if (res.errno == "0"){
                    // 刷新当前界面
                    location.reload();
                }else{
                    $error.html(res.errmsg).show();
                }
            }

        })
    })
})