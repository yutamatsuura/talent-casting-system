$(function () {
  /* ===============================
   * Drawer
   * =============================== */
  const $drawer = $(".drawer");
  $drawer.drawer();

  $(".drawer-nav-main a").on("click", () => {
    $drawer.drawer("close");
  });

  /* ===============================
   * FAQ アコーディオン
   * =============================== */
  $(".faq-ttl").on("click", function () {
    $(this)
      .toggleClass("show")
      .next(".faq-content")
      .slideToggle()
      .parent()
      .toggleClass("is-active");
  });

  /* ===============================
   * nagare-box（スマホのみ slick）
   * =============================== */
  function initNagareSlick() {
    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    const $target = $(".nagare-box ul");

    if (isMobile && !$target.hasClass("slick-initialized")) {
      $target.slick({
        infinite: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        autoplay: false,
        pauseOnHover: false,
        centerMode: true,
        centerPadding: "7.5%",
      });
    } else if (!isMobile && $target.hasClass("slick-initialized")) {
      // PCになったら unslick して通常表示に戻す
      $target.slick("unslick");
    }
  }

  const menuItems = document.querySelectorAll(".menu-item");
  const slides = document.querySelectorAll(".slide");

  menuItems.forEach((item) => {
    item.addEventListener("click", () => {
      const target = item.dataset.target;

      // メニューの active 切替
      menuItems.forEach((i) => i.classList.remove("active"));
      item.classList.add("active");

      // スライドの active 切替
      slides.forEach((slide) => {
        slide.classList.remove("active");
        if (slide.dataset.slide === target) {
          slide.classList.add("active");
        }
      });
    });
  });

  initNagareSlick();
  $(window).on("resize", initNagareSlick);

  /* ===============================
   * スムーススクロール
   * =============================== */
  $(document).on("click", 'a[href^="#"]:not([href="#"])', function (e) {
    e.preventDefault();
    const target = $($(this).attr("href"));
    if (!target.length) return;

    $("html").animate({ scrollTop: target.offset().top }, 400, "swing");
  });
});
