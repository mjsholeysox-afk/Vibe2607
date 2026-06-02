// ==================== 모바일 메뉴 ==================== 
const hamburger = document.getElementById('hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // 메뉴 항목 클릭 시 메뉴 닫기
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });
}

// ==================== 폼 제출 ==================== 
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();

        // 간단한 유효성 검사
        if (!name || !email || !message) {
            alert('모든 필드를 입력해주세요.');
            return;
        }

        // 이메일 형식 검사
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('올바른 이메일 형식을 입력해주세요.');
            return;
        }

        // 성공 메시지
        alert(`감사합니다 ${name}님! 메시지가 전송되었습니다.\n곧 연락드리겠습니다.`);

        // 폼 초기화
        contactForm.reset();
    });
}

// ==================== 스크롤 애니메이션 ==================== 
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// 스킬 카드와 프로젝트 카드에 애니메이션 적용
const skillCards = document.querySelectorAll('.skill-card');
const projectCards = document.querySelectorAll('.project-card');

skillCards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.animation = `fadeInUp 0.8s ease ${index * 0.1}s forwards`;
    observer.observe(card);
});

projectCards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.animation = `fadeInUp 0.8s ease ${index * 0.1}s forwards`;
    observer.observe(card);
});

// ==================== 네비게이션 강조 ==================== 
window.addEventListener('scroll', () => {
    const navLinks = document.querySelectorAll('.nav-menu a');
    const sections = document.querySelectorAll('section');

    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (window.scrollY >= sectionTop - 60) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.style.color = '';
        if (link.getAttribute('href').includes(current)) {
            link.style.color = 'var(--primary-color)';
        }
    });
});

// ==================== 페이지 로드 애니메이션 ==================== 
window.addEventListener('load', () => {
    // 페이지 로드 완료 시 실행되는 추가 초기화
    console.log('포트폴리오 페이지 로드 완료!');
});

// ==================== 부드러운 스크롤 ==================== 
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== 동적 연도 업데이트 ==================== 
const year = new Date().getFullYear();
const footerText = document.querySelector('.footer p');
if (footerText) {
    footerText.textContent = `© ${year} 문종순. All rights reserved.`;
}

// ==================== 스크롤 진행도 표시 ==================== 
window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;

    // 필요시 진행도 바를 추가할 수 있습니다
});

// ==================== 추가 기능: 카운터 애니메이션 ==================== 
const animateCounter = (element, target, duration = 2000) => {
    let current = 0;
    const increment = target / (duration / 16);
    const counter = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(counter);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
};

// 통계 카운터 애니메이션
const statNumbers = document.querySelectorAll('.stat-number');
let counted = false;

const countObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !counted) {
        statNumbers.forEach(num => {
            const target = parseInt(num.textContent);
            if (!isNaN(target)) {
                animateCounter(num, target);
            }
        });
        counted = true;
        countObserver.unobserve(entries[0].target);
    }
}, { threshold: 0.5 });

if (statNumbers.length > 0) {
    countObserver.observe(statNumbers[0].parentElement.parentElement);
}
