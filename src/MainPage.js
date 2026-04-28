import React from 'react';
import Layout from './Layout';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import {
  HeroSection,
  StyledSlider,
  ContentCard,
  PosterImage,
  ContentTitle,
  RecommendationSection,
  RecommendationSlider,
  PosterCard,
  SmallPosterImage,
  SmallContentTitle
} from './MainPage.styles';


const topContent = [
  { id: 1, title: "TOP 1" },
  { id: 2, title: "TOP 2" },
  { id: 3, title: "TOP 3" },
  { id: 4, title: "TOP 4" },
  { id: 5, title: "TOP 5" }
];

const recentRecommendations = [
  { 
    id: 1, 
    title: "압꾸정",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/6QXfrZWYS5cPlmNsIhpofW5R3ct.jpg"
  },
  { 
    id: 2, 
    title: "런닝맨",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/15SMnscZqd7HZ0bzruatOcKUlOV.jpg"
  },
  { 
    id: 3, 
    title: "나 혼자 산다",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/bq3Emv3pJLUyHvwGqiAXRwJvAmL.jpg"
  },
  { 
    id: 4, 
    title: "악귀",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/uLqu0gCPKyC7IXCh9mTrkaXPBD8.jpg"
  },
  { 
    id: 5, 
    title: "그것이 알고 싶다",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/pYCWmCNoKl7rJzK6VWiOZj7Xwmu.jpg"
  },
  { 
    id: 6, 
    title: "원피스",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/qHjXsSUuolEtbgvYPzRjAuB1VHE.jpg"
  },
  { 
    id: 7, 
    title: "이상한 변호사 우영우",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/yv57TccCkgdy3St7rspBPKROeRK.jpg"
  },
  { 
    id: 8, 
    title: "아바타",
    posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/m5lCha2XcbDowDoYHPc0DTNaCPU.jpg"
  }
];

const genreRecommendations = [
  { id: 1, title: "추천 컨텐츠 1" },
  { id: 2, title: "추천 컨텐츠 2" },
  { id: 3, title: "추천 컨텐츠 3" },
  { id: 4, title: "추천 컨텐츠 4" },
  { id: 5, title: "추천 컨텐츠 5" },
  { id: 6, title: "추천 컨텐츠 6" },
  { id: 7, title: "추천 컨텐츠 7" },
  { id: 8, title: "추천 컨텐츠 8" }
];

const sliderSettings = {
  dots: true,
  infinite: true,
  speed: 500,
  slidesToShow: 1,
  slidesToScroll: 1,
  arrows: true,
  autoplay: true,
  autoplaySpeed: 3000
};

const recommendationSettings = {
  dots: false,
  infinite: false,
  speed: 500,
  slidesToShow: 5,
  slidesToScroll: 2,
  arrows: true,
  responsive: [
    {
      breakpoint: 1024,
      settings: {
        slidesToShow: 4,
        slidesToScroll: 2,
      }
    },
    {
      breakpoint: 768,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 1,
      }
    },
    {
      breakpoint: 480,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 1,
      }
    }
  ]
};

export default function MainPage() {
  return (
    <Layout>
      <HeroSection>
        <h2>이번 주 TOP 5</h2>
        <StyledSlider {...sliderSettings}>
          {topContent.map(item => (
            <ContentCard key={item.id}>
              <PosterImage />
              <ContentTitle>{item.title}</ContentTitle>
            </ContentCard>
          ))}
        </StyledSlider>
      </HeroSection>

      <RecommendationSection>
        <h2>최근 기록 기반 추천</h2>
        <RecommendationSlider {...recommendationSettings}>
          {recentRecommendations.map(item => (
            <PosterCard key={item.id}>
              <SmallPosterImage posterUrl={item.posterUrl} />
              <SmallContentTitle>{item.title}</SmallContentTitle>
            </PosterCard>
          ))}
        </RecommendationSlider>
      </RecommendationSection>

      <RecommendationSection>
        <h2>장르별 추천</h2>
        <RecommendationSlider {...recommendationSettings}>
          {genreRecommendations.map(item => (
            <PosterCard key={item.id}>
              <SmallPosterImage posterUrl={item.posterUrl} />
              <SmallContentTitle>{item.title}</SmallContentTitle>
            </PosterCard>
          ))}
        </RecommendationSlider>
      </RecommendationSection>
    </Layout>
  );
}











// const GlobalStyle = createGlobalStyle`
//   html, body {
//     margin: 0;
//     padding: 0;
//     width: 100%;
//     min-height: 100vh;
//     background-color: ${props => props.theme.body};
//     color: ${props => props.theme.text};
//     transition: all 0.3s ease;
//   }

//   #root {
//     min-height: 100vh;
//     background-color: ${props => props.theme.body};
//   }
// `;

// const MainContainer = styled.div`
//   max-width: 75%;
//   margin: 0 auto;
//   padding: 0 20px;
//   min-height: 100vh;
//   color: ${props => props.theme.text};
//   transition: all 0.3s ease;
// `;

// const BrandContainer = styled.div`
//   display: flex;
//   flex-direction: column;  // 세로 방향으로 변경
// `;

// const ThemeToggle = styled.button`
//   background: none;
//   border: none;
//   color: ${props => props.theme.text};
//   cursor: pointer;
//   padding: 12px;
//   font-size: 1.5rem;
//   display: flex;
//   align-items: center;
//   justify-content: center;
//   transition: transform 0.2s;
  
//   &:hover {
//     color: ${props => props.theme.hover};
//     transform: scale(1.1);
//   }
// `;

// const Header = styled.header`
//   padding: 20px 0;
//   border-bottom: 1px solid ${props => props.theme.headerBorder};
// `;

// const HeaderContent = styled.div`
//   display: flex;
//   justify-content: space-between;
//   align-items: center;
// `;

// const Nav = styled.nav`
//   ul {
//     display: flex;
//     list-style: none;
//     gap: 30px;
//     margin: 0;
//     padding: 0;
//     align-items: center;
//   }
  
//   a {
//     text-decoration: none;
//     color: ${props => props.theme.text};
//     &:hover {
//       color: ${props => props.theme.hover};
//     }
//   }

//   li {
//     font-size: 1.1rem;
//     display: flex;
//     align-items: center;
//   }
// `;

// const HeroSection = styled.section`
//   text-align: center;
//   padding: 30px 0;  
  
//   h2 {
//     margin-bottom: 40px;
//     font-size: 2rem;
//     color: ${props => props.theme.text};
//   }
// `;

// const StyledSlider = styled(Slider)`
//   width: 100%;
//   max-width: 100%;   
//   margin: 0 auto;
//   position: relative;
//   display: grid;
//   grid-template-columns: 50px 1fr 50px;
//   align-items: center;
//   gap: 10px;

//   .slick-prev {
//     grid-column: 1;
//     width: 40px;
//     height: 40px;
//     z-index: 1;
//     left: 30px;

//     &::before {
//       font-size: 40px;
//       color: rgba(199, 8, 81, 0.85);
//       opacity: 0.8;
//     }
//     &:hover::before {
//       color: rgb(199, 8, 81);
//       opacity: 1;
//     }
//   }

//   .slick-next {
//     grid-column: 3;
//     width: 40px;
//     height: 40px;
//     z-index: 1;
//     right: 30px;

//     &::before {
//       font-size: 40px;
//       color: rgba(199, 8, 81, 0.85);
//       opacity: 0.8;
//     }
//     &:hover::before {
//       color: rgb(199, 8, 81);
//       opacity: 1;
//     }
//   }

//   .slick-list {
//     grid-column: 2;
//     width: 100%;
//     overflow: hidden;
//   }

//   .slick-track {
//     display: flex;
//     align-items: center;
//   }

//   .slick-slide {
//     > div {
//       display: flex;
//       justify-content: center;
//     }
//   }

//   .slick-dots {
//     bottom: 0px;
    
//     li {
//       button:before {
//         color: ${props => props.theme.text};
//       }
//       &.slick-active button:before {
//         color: rgb(199, 8, 81);
//       }
//     }
//   }
// `;

// const ContentCard = styled.div`
//   width: 100%;
//   display: flex;
//   justify-content: center;   
//   align-items: center;       
//   flex-direction: column;
//   padding: 20px;
//   margin: 0 auto;
//   text-align: center;
// `;

// const PosterImage = styled.div`
//   width: 95%;
//   max-width: 100%;  
//   padding-top: 60%;
//   background-color: #ddd;
//   border-radius: 8px;
//   background-size: cover;
//   background-position: center;
//   box-shadow: 0 4px 8px rgba(0,0,0,0.1);
//   transition: transform 0.2s;
//   transform-origin: center center;
//   margin: 0 auto;
//   position: relative;
  
//   &:hover {
//     transform: scale(1.02);
//   }
//   background-color: ${props => props.theme.cardBg};
//   box-shadow: 0 4px 8px ${props => props.theme.shadow};
// `;

// const ContentTitle = styled.h4`
//   padding: 40px 0;
//   margin: 0;
//   text-align: center;
//   font-size: 1.5rem;
//   color: ${props => props.theme.text};
//   width: 100%;
//   position: relative;
//   left: 0; 
// `;

// const BrandTitle = styled.h1`
//   font-family: 'Pacifico', cursive;
//   font-size: 2rem;
//   color: ${props => props.theme.text};

//   a {
//     text-decoration: none;
//     color: inherit;
    
//     &:hover {
//       text-decoration: none;
//       color: inherit;
//     }
//   }


//   span {
//     color:rgb(199, 8, 81); // LG 핼로비전 색상
//   }
// `;

// const NavIcon = styled.span`
//   margin-right: 5px;
// `;

// const Footer = styled.footer`
//   text-align: center;
//   padding: 20px 0;
//   margin-top: 40px;
//   border-top: 1px solid ${props => props.theme.headerBorder};
//   color: ${props => props.theme.text};
// `;

// const RecommendationSection = styled.section`
//   padding: 30px 0;
  
//   h2 {
//     text-align: left;
//     font-size: 2rem;
//     color: ${props => props.theme.text};
//     margin-bottom: 30px;
//     padding-left: 60px;
//   }
// `;

// const RecommendationSlider = styled(Slider)`
//   width: 90%;
//   margin: 0 auto;

//   .slick-prev, .slick-next {
//     width: 40px;
//     height: 40px;
//     z-index: 1;
//     top: 40%;  // 상단으로 위치 조정
//     &:before {
//       font-size: 40px;
//       color: rgba(199, 8, 81, 0.85);  // 투명도 증가로 더 옅은 색상
//       opacity: 0.8;
//     }
//     &:hover:before {
//       color: rgb(199, 8, 81);  // 호버시 원래 색상으로
//       opacity: 1;
//     }
//   }
  
//   .slick-prev {
//     left: -45px;
//   }
  
//   .slick-next {
//     right: -45px;
//   }

//   .slick-track {
//     display: flex;
//     gap: 20px;
//   }

//   .slick-slide {
//     > div {
//       margin: 0 10px;
//     }
//   }
// `;



// const PosterCard = styled.div`
//   flex: 0 0 auto;
//   width: 200px;
//   transition: transform 0.2s;
  
//   &:hover {
//     transform: translateY(-5px);
//   }
// `;

// const SmallPosterImage = styled.div`
//   width: 100%;
//   padding-top: 150%; // 2:3 비율을 위해 width의 150%로 설정
//   background-color: #ddd;
//   border-radius: 8px;
//   background-size: cover;
//   background-position: center;
//   background-image: url(${props => props.posterUrl});
//   box-shadow: 0 4px 8px rgba(0,0,0,0.1);
//   position: relative;
//   background-color: ${props => props.theme.cardBg};
//   box-shadow: 0 4px 8px ${props => props.theme.shadow};
// `;

// const SmallContentTitle = styled.h4`
//   padding: 10px 0;
//   margin: 0;
//   text-align: center;
//   font-size: 1rem;
//   color: ${props => props.theme.text};
// `;


// const SearchOverlay = styled.div`
//   position: fixed;
//   top: 0;
//   left: 0;
//   width: 100%;
//   height: 100%;
//   background-color: rgba(0, 0, 0, 0.5);  // 더 어두운 배경으로 변경
//   display: ${props => props.isOpen ? 'flex' : 'none'};
//   justify-content: center;
//   align-items: flex-start;
//   padding-top: 100px;
//   z-index: 1000;
// `;

// const SearchContainer = styled.div`
//   width: 800px;  
//   padding: 40px;  
//   background-color: ${props => props.theme.cardBg};
//   border-radius: 8px;
//   box-shadow: 0 4px 12px ${props => props.theme.shadow};
// `;

// const SearchInput = styled.input`
//   width: 100%;
//   padding: 15px;
//   font-size: 1.2rem;
//   border: 2px solid ${props => props.theme.headerBorder};
//   border-radius: 4px;
//   background-color: ${props => props.theme.body};
//   color: ${props => props.theme.text};
//   outline: none;
//   box-sizing: border-box;      
//   display: block;              
//   margin: 0 auto;             

//   &:focus {
//     border-color: ${props => props.theme.hover};
//   }
// `;



// const MainPage = () => {
//   const { isDark, toggleTheme } = useContext(ThemeContext);
//   const [isSearchOpen, setIsSearchOpen] = useState(false);
//   const [searchQuery, setSearchQuery] = useState('');
  
//   const recentRecommendations = [
//     { 
//       id: 1, 
//       title: "압꾸정",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/6QXfrZWYS5cPlmNsIhpofW5R3ct.jpg"
//     },
//     { 
//       id: 2, 
//       title: "런닝맨",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/15SMnscZqd7HZ0bzruatOcKUlOV.jpg"
//     },
//     { 
//       id: 3, 
//       title: "나 혼자 산다",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/bq3Emv3pJLUyHvwGqiAXRwJvAmL.jpg"
//     },
//     { 
//       id: 4, 
//       title: "악귀",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/uLqu0gCPKyC7IXCh9mTrkaXPBD8.jpg"
//     },
//     { 
//       id: 5, 
//       title: "그것이 알고 싶다",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/pYCWmCNoKl7rJzK6VWiOZj7Xwmu.jpg"
//     },
//     { 
//       id: 6, 
//       title: "원피스",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/qHjXsSUuolEtbgvYPzRjAuB1VHE.jpg"
//     },
//     { 
//       id: 7, 
//       title: "이상한 변호사 우영우",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/yv57TccCkgdy3St7rspBPKROeRK.jpg"
//     },
//     { 
//       id: 8, 
//       title: "아바타",
//       posterUrl: "https://media.themoviedb.org/t/p/w600_and_h900_bestv2/m5lCha2XcbDowDoYHPc0DTNaCPU.jpg"
//     }
//   ];


//   // 검색창 열기/닫기 핸들러
//   const toggleSearch = () => {
//     setIsSearchOpen(!isSearchOpen);
//   };

//   // 검색어 입력 핸들러
//   const handleSearchChange = (e) => {
//     setSearchQuery(e.target.value);
//   };

//   // ESC 키로 검색창 닫기
//   useEffect(() => {
//     const handleEsc = (e) => {
//       if (e.key === 'Escape') {
//         setIsSearchOpen(false);
//       }
//     };
//     window.addEventListener('keydown', handleEsc);
//     return () => window.removeEventListener('keydown', handleEsc);
//   }, []);
  
//   const sliderSettings = {
//     dots: true,
//     infinite: true,
//     speed: 500,
//     slidesToShow: 1,
//     slidesToScroll: 1,
//     arrows: true,
//     autoplay: true,
//     autoplaySpeed: 3000
//   };

//   const recommendationSettings = {
//     dots: false,
//     infinite: false,
//     speed: 500,
//     slidesToShow: 5,
//     slidesToScroll: 2,
//     arrows: true,
//     responsive: [
//       {
//         breakpoint: 1024,
//         settings: {
//           slidesToShow: 4,
//           slidesToScroll: 2,
//         }
//       },
//       {
//         breakpoint: 768,
//         settings: {
//           slidesToShow: 3,
//           slidesToScroll: 1,
//         }
//       },
//       {
//         breakpoint: 480,
//         settings: {
//           slidesToShow: 2,
//           slidesToScroll: 1,
//         }
//       }
//     ]
//   };

//   const topContent = [
//     { id: 1, title: "TOP 1" },
//     { id: 2, title: "TOP 2" },
//     { id: 3, title: "TOP 3" },
//     { id: 4, title: "TOP 4" },
//     { id: 5, title: "TOP 5" }
//   ];

//   // const recentRecommendations = [
//   //   { id: 1, title: "추천 컨텐츠 1" },
//   //   { id: 2, title: "추천 컨텐츠 2" },
//   //   { id: 3, title: "추천 컨텐츠 3" },
//   //   { id: 4, title: "추천 컨텐츠 4" },
//   //   { id: 5, title: "추천 컨텐츠 5" },
//   //   { id: 6, title: "추천 컨텐츠 6" },
//   //   { id: 7, title: "추천 컨텐츠 7" },
//   //   { id: 8, title: "추천 컨텐츠 8" }
//   // ];

//   const genreRecommendations = [
//     { id: 1, title: "추천 컨텐츠 1" },
//     { id: 2, title: "추천 컨텐츠 2" },
//     { id: 3, title: "추천 컨텐츠 3" },
//     { id: 4, title: "추천 컨텐츠 4" },
//     { id: 5, title: "추천 컨텐츠 5" },
//     { id: 6, title: "추천 컨텐츠 6" },
//     { id: 7, title: "추천 컨텐츠 7" },
//     { id: 8, title: "추천 컨텐츠 8" }
//   ];

//   return (
//     <StyledThemeProvider theme={isDark ? darkTheme : lightTheme}>
//       <GlobalStyle />
//       <MainContainer>
//         <SearchOverlay isOpen={isSearchOpen} onClick={() => setIsSearchOpen(false)}>
//           <SearchContainer onClick={e => e.stopPropagation()}>
//             <SearchInput
//               type="text"
//               placeholder="검색어를 입력하세요..."
//               value={searchQuery}
//               onChange={handleSearchChange}
//               autoFocus
//             />
//           </SearchContainer>
//         </SearchOverlay>

//         <Header>
//           <HeaderContent>
//             <BrandContainer>
//               <BrandTitle>
//                 <Link to="/main">
//                   <span>O</span>ptimal <span>P</span>ick <span>S</span>ystem
//                 </Link>
//               </BrandTitle>
//             </BrandContainer>
//             <Nav>
//               <ul>
//                 <li>
//                   <a href="#" onClick={(e) => {
//                     e.preventDefault();
//                     toggleSearch();
//                   }}>
//                     <NavIcon>
//                       <FontAwesomeIcon icon={faSearch} />
//                     </NavIcon>
//                   </a>
//                 </li>
//                 <li><Link to="/main">홈</Link></li>
//                 <li><Link to="/mypage">마이페이지</Link></li>
//                 <li>
//                   <ThemeToggle onClick={toggleTheme}>
//                     <FontAwesomeIcon icon={isDark ? faSun : faMoon} />
//                   </ThemeToggle>
//                 </li>
//               </ul>
//             </Nav>
//           </HeaderContent>
//         </Header>

//         <HeroSection>
//           <h2>이번 주 TOP 5</h2>
//           <StyledSlider {...sliderSettings}>
//             {topContent.map((content) => (
//               <ContentCard key={content.id}>
//                 <PosterImage />
//                 <ContentTitle>{content.title}</ContentTitle>
//               </ContentCard>
//             ))}
//           </StyledSlider>
//         </HeroSection>
        
//         <RecommendationSection>
//           <h2>최근 기록 기반 추천</h2>
//           <RecommendationSlider {...recommendationSettings}>
//             {recentRecommendations.map((item) => (
//               <PosterCard key={item.id}>
//                 <SmallPosterImage posterUrl={item.posterUrl} />
//                 <SmallContentTitle>{item.title}</SmallContentTitle>
//               </PosterCard>
//             ))}
//           </RecommendationSlider>
//         </RecommendationSection>   

//         <RecommendationSection>
//           <h2>장르별 추천</h2>
//           <RecommendationSlider {...recommendationSettings}>
//             {genreRecommendations.map((item) => (
//               <PosterCard key={item.id}>
//                 <SmallPosterImage />
//                 <SmallContentTitle>{item.title}</SmallContentTitle>
//               </PosterCard>
//             ))}
//           </RecommendationSlider>
//         </RecommendationSection>

        

//         <Footer>
//           <p>&copy; 2025 Optimal Pick System. All rights reserved.</p>
//         </Footer>
//       </MainContainer>
//     </StyledThemeProvider>
//   );
// };

// export default MainPage;