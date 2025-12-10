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
  const slides = document.querySelectorAll(".tablet .slide");

  let currentIndex = 0;
  let autoPlayTimer = null;
  let intervalTime = 3000; // ★ 切り替え秒数（ミリ秒）ここを変更する

  // スライド切り替え処理
  function showSlide(index) {
    const target = slides[index].dataset.slide;

    // メニュー active
    menuItems.forEach((m) => m.classList.remove("active"));
    document
      .querySelector(`.menu-item[data-target="${target}"]`)
      .classList.add("active");

    // スライド active
    slides.forEach((s) => s.classList.remove("active"));
    slides[index].classList.add("active");

    currentIndex = index;
  }

  // 自動再生スタート
  function startAutoPlay() {
    stopAutoPlay(); // 二重起動防止
    autoPlayTimer = setInterval(() => {
      let next = (currentIndex + 1) % slides.length;
      showSlide(next);
    }, intervalTime);
  }

  // 停止
  function stopAutoPlay() {
    if (autoPlayTimer) {
      clearInterval(autoPlayTimer);
    }
  }

  // メニュークリック
  menuItems.forEach((item, idx) => {
    item.addEventListener("click", () => {
      showSlide(idx);
      startAutoPlay(); // クリック後も自動再生続行
    });
  });

  // 初期表示とスタート
  showSlide(0);
  startAutoPlay();

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
