var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 更新首页新闻数据
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        // 获取被点击的分类id
        var clickCid = $(this).attr('data-cid');
        // 遍历所有li标签，并移除class类名
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        // 给当前被点击的分类id添加class类名
        $(this).addClass('active');
        // 如果点击的分类id不是当前id时
        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;

            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            // data_querying = false;
            updateNewsData()
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (!data_querying){
                // 将是否正在向后台获取新闻数据的标志设置为true
                data_querying = true;
                // 如果当前页数还没到达总页数
                if (cur_page < total_page){
                    // 向后端发送请求，获取下一页的新闻数据
                    updateNewsData();
                    cur_page += 1;
                }else{
                    data_querying = false;
                }
            }
        }
    })
});

function updateNewsData() {
    // 更新新闻数据
    var params = {
        "page": 1,
        "cid": currentCid,
        "per_page": 10
    };

    $.get("/news_list", params, function (res) {
        // 设置 数据正在加载 变量为false，以便下次上拉加载
            data_querying = false;
        if (res.errno == "0") {
            // alert(res.data.cid);
            // console.log(res.data);

            total_page = res.data.total_page;
            if (cur_page == 1){
                // 先清空原有新闻数据
                $(".list_con").html('');
            }

            // 显示数据
            for (var i = 0; i < res.data.news_li.length; i++) {
                var news = res.data.news_li[i];
                var content = '<li>';
                content += '<a href="/news/' + news.id + '" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>';
                content += '<a href="/news/' + news.id + '" class="news_title fl">' + news.title + '</a>';
                content += '<a href="/news/' + news.id + '" class="news_detail fl">' + news.digest + '</a>';
                content += '<div class="author_info fl">';
                content += '<div class="source fl">来源：' + news.source + '</div>';
                content += '<div class="time fl">' + news.create_time + '</div>';
                content += '</div>';
                content += '</li>';
                $(".list_con").append(content);
            }
        }
    });

}
