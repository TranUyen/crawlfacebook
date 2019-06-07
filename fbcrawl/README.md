Scrapy là một framework được viết bằng Python, nó cấp sẵn 1 cấu trúc tương đối hoàn chỉnh để thực hiện việc crawl và extract data từ website một cách nhanh chóng và dễ dàng.
Ưu điểm của Scrapy là cung cấp sẵn 1 cấu trúc tương đối hoàn chỉnh để thực hiện việc crawl và scrape data, người dùng chỉ cần bổ sung thêm định nghĩa về dữ liệu cần lấy là xong (ví dụ như URL bắt đầu là gì, link chuyển qua trang mới là gì, các thông tin cần lấy ở mỗi trang là gì).
Thành phần của Scrapy:

Scrapy Engine: có trách nhiệm kiểm soát luồng dữ liệu giữa tất cả các thành phần của hệ thống và kích hoạt các sự kiện khi một số hành động xảy ra
Scheduler: Giống như một hàng đợi (queue), scheduler sắp xếp thứ tự các URL cần download
Dowloader: Thực hiện dowload trang web và cung cấp cho engine
Spiders: là class được viết bởi người dùng, chúng có trách nhiệm bóc tách dữ liệu cần thiết và tạo các url mới để nạp lại cho scheduler qua engine.
Item Pipeline: những dữ liệu được bóc tách từ spiders sẽ đưa tới đây, Item pipeline có nhiệm vụ xử lý chúng và lưu vào cơ sở dữ liệu
Các Middlewares: Là các thành phần nằm giữa Engine với các thành phần khác, chúng đều có mục địch là giúp người dùng có thể tùy biến, mở rổng khả năng xử lý cho các thành phần.
+  Spider middlewares
Là thành phần nằm giữa Eninge và Spiders, chúng xử lý các response đầu vào của Spiders và đầu ra (item và các url mới).
+ Dowloader middlewares
Nằm giữa Engine và Dowloader, chúng xử lý các request được đẩy vào từ Engine và các response được tạo ra từ Dowloader
+  Scheduler middlewares
Nằm giữa Engine và Scheduler để xử lý những requests giữa hai thành phần
1.2  Splash Framework
Splash là một dịch vụ kết xuất javascript. Đó là một trình duyệt web nhẹ với API HTTP, được triển khai trong Python 3 bằng cách sử dụng Twisted và QT5
Một số tính năng của Splash:
• xử lý song song nhiều trang web;
• nhận kết quả HTML và / hoặc chụp ảnh màn hình;
• TẮT hình ảnh hoặc sử dụng quy tắc Adblock Plus để hiển thị nhanh hơn;
• thực thi JavaScript tùy chỉnh trong ngữ cảnh trang;
• viết kịch bản duyệt Lua ;
• phát triển các kịch bản Splash Lua trong Splash-Jupyter Notebooks.
• nhận thông tin kết xuất chi tiết ở định dạng HAR.


1. Cách thức thực hiện
Project fbcrawl gồm các lớp và thư mục:

Trong thư mục spiders gồm :

Fbcrawl.py:

Trên init, nó điều hướng đến mbasic.facebook.com và đăng nhập vào facebook theo được cung cấp credentials, được chuyển dưới dạng tham số tại thời điểm thực hiện. 
Sau đó, parse_page phương thức được gọi với page tên được đưa ra trong thời gian chạy và quá trình thu thập thông tin bắt đầu truy xuất đệ quy tất cả các bài đăng được tìm thấy trong mỗi trang.
Đối với mỗi bài đăng, nó lấy tất cả các tính năng, sử dụng hàm gọi lại parse_post và tất cả các phản ứng, sử dụng parse_reactions.
Trang web được phân tích cú pháp và các trường được trích xuất bằng bộ chọn XPath . Các bộ chọn này được thực hiện trên lib python lxmlnên chúng rất nhanh.
Nhờ XPath, scrapy có thể điều hướng trang web theo mô hình DOM, vì người ta sẽ điều hướng một hệ thống tệp, với một số tính năng khớp mẫu. Nếu bạn không biết gì về XPath 
XPath có thể dễ dàng có được bằng cách sử dụng các công cụ dev của Firefox hoặc Chrom
group.py: lấy thông tin của group
comment.py:  lấy comment của bài viết

items.py: 
Tệp này định nghĩa items class, để các trường trích xuất có thể được nhóm trong các items và được sắp xếp một cách ngắn gọn hơn. Các dữ liệu thu thập được sẽ được xuất ra file CSV.

Phần III:  Cài đặt 
1. Cách cài đặt Scrapy 
Sử dụng câu lệnh : pip install scrapy
Để chắc chắn cài đặt thành công kiểm tra:  


Phần IV:  Hướng dẫn sử dụng 
1. Hướng dẫn chạy project fbcrawl
• Lấy thông tin của Page
Nhập lênh:
scrapy crawl fb -a email="EMAILTOLOGIN" -a password="PASSWORDTOLOGIN" -a page="NAMEOFTHEPAGETOCRAWL" -a year="2015" -a lang="it" -o namefile.csv

EMAILTOLOGIN : email tài khoản cá nhân
PASSWORDTOLOGIN: password tài khoản của bạn
Year là năm: lấy tất cả các bài viết từ hiện tại đến năm mà bạn nhập vào, nếu không có năm thì là 2018
Lang: là lựa chọn ngôn ngữ
Namefile.csv: là tên file csv là bạn muốn xuất dữ liệu ra
Kết quả thu được: 

Thông tin lấy được: 
- Source: tên page
- Date: ngày tháng đăng bài viết
- Text: nội dung bài đăng
- Reaction: số lượng react gồm: số lượt like, haha, love, wow ,sigh, grrr 
- Comments: số lượng comments
- url: link đến mỗi bài viết


• Lấy thông tin group
Nhập lệnh:
scrapy crawl fbgroup -a email="EMAILTOLOGIN" -a password="PASSWORDTOLOGIN" -a group="groups/NAMEOFTHEPAGETOCRAWL"  -a lang="it" -o namefile.csv

Kết quả thu thập được:


Các thông tin giống page nhưng có thêm:
Membersgroup: số thành viên của group
Photosgroup: tổng số ảnh của bài viết
Source: người đăng bài
• Cách lấy comment:
Nhập lệnh 	
scrapy crawl comments -a email="EMAILTOLOGIN" -a password="PASSWORDTOLOGIN" -a page="LINKOFTHEPOSTTOCRAWL" -o DUMPFILE.csv

Kết quả thu thập được:
Source: người bình luận
Reply_to: người repply bình luận
Date: ngày bình luận
Reactions: cảm xúc bày tỏ
Text: nội dung bình luận



