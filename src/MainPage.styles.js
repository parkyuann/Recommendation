import { createGlobalStyle, styled } from 'styled-components';
import Slider from 'react-slick';

export const GlobalStyle = createGlobalStyle`
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    min-height: 100vh;
    background-color: ${props => props.theme.body};
    color: ${props => props.theme.text};
    transition: all 0.3s ease;
  }

  #root {
    min-height: 100vh;
    background-color: ${props => props.theme.body};
  }
`;

export const MainContainer = styled.div`
  max-width: 75%;
  margin: 0 auto;
  padding: 0 20px;
  min-height: 100vh;
  color: ${props => props.theme.text};
  transition: all 0.3s ease;
`;

export const Header = styled.header`
  padding: 20px 0;
  border-bottom: 1px solid ${props => props.theme.headerBorder};
`;

export const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const BrandContainer = styled.div`
  display: flex;
  flex-direction: column;  // 세로 방향으로 변경
`;

export const BrandTitle = styled.h1`
  font-family: 'Pacifico', cursive;
  font-size: 2rem;
  color: ${props => props.theme.text};

  a {
    text-decoration: none;
    color: inherit;
    
    &:hover {
      text-decoration: none;
      color: inherit;
    }
  }

  span {
    color:rgb(199, 8, 81); // LG 핼로비전 색상
  }
`;

export const Nav = styled.nav`
  ul {
    display: flex;
    list-style: none;
    gap: 30px;
    margin: 0;
    padding: 0;
    align-items: center;
  }
  
  a {
    text-decoration: none;
    color: ${props => props.theme.text};
    &:hover {
      color: ${props => props.theme.hover};
    }
  }

  li {
    font-size: 1.3rem;
    display: flex;
    align-items: center;
  }
`;

export const NavIcon = styled.span`
  display: inline-block;       /* inline-block으로 바꿔야 위치 속성이 먹습니다 */
  margin-right: 5px;
  position: relative;          /* 상대 위치 지정 */
  top: 2px;
  color: ${({ theme }) => theme.text};
  font-size: 1.5rem;            
  transition: color 0.2s ease;  

  &:hover {
    color: ${({ theme }) => theme.hover};
  }
`;


export const ThemeToggle = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.text};
  cursor: pointer;
  padding: 12px;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  
  &:hover {
    color: ${props => props.theme.hover};
    transform: scale(1.1);
  }
`;

export const Footer = styled.footer`
  text-align: center;
  padding: 20px 0;
  margin-top: 40px;
  border-top: 1px solid ${props => props.theme.headerBorder};
  color: ${props => props.theme.text};
`;

export const SearchOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);  // 더 어두운 배경으로 변경
  display: ${props => props.isOpen ? 'flex' : 'none'};
  justify-content: center;
  align-items: flex-start;
  padding-top: 100px;
  z-index: 1000;
`;

export const SearchContainer = styled.div`
  width: 800px;  
  padding: 40px;  
  background-color: ${props => props.theme.cardBg};
  border-radius: 8px;
  box-shadow: 0 4px 12px ${props => props.theme.shadow};
`;

export const SearchInput = styled.input`
  width: 100%;
  padding: 15px;
  font-size: 1.2rem;
  border: 2px solid ${props => props.theme.headerBorder};
  border-radius: 4px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  outline: none;
  box-sizing: border-box;      
  display: block;              
  margin: 0 auto;             

  &:focus {
    border-color: ${props => props.theme.hover};
  }
`;

export const HeroSection = styled.section`
  text-align: center;
  padding: 30px 0;  
  
  h2 {
    margin-bottom: 40px;
    font-size: 2rem;
    color: ${props => props.theme.text};
  }
`;


export const StyledSlider = styled(Slider)`
  width: 100%;
  max-width: 100%;   
  margin: 0 auto;
  position: relative;
  display: grid;
  grid-template-columns: 50px 1fr 50px;
  align-items: center;
  gap: 10px;

  .slick-prev {
    grid-column: 1;
    width: 40px;
    height: 40px;
    z-index: 1;
    left: 30px;

    &::before {
      font-size: 30px;
      color: rgba(199, 8, 81, 0.85);
      opacity: 0.8;
    }
    &:hover::before {
      color: rgb(199, 8, 81);
      opacity: 1;
    }
  }

  .slick-next {
    grid-column: 3;
    width: 40px;
    height: 40px;
    z-index: 1;
    right: 30px;

    &::before {
      font-size: 30px;
      color: rgba(199, 8, 81, 0.85);
      opacity: 0.8;
    }
    &:hover::before {
      color: rgb(199, 8, 81);
      opacity: 1;
    }
  }

  .slick-list {
    grid-column: 2;
    width: 100%;
    overflow: hidden;
  }

  .slick-track {
    display: flex;
    align-items: center;
  }

  .slick-slide {
    > div {
      display: flex;
      justify-content: center;
    }
  }

  .slick-dots {
    bottom: 0px;
    
    li {
      button:before {
        color: ${props => props.theme.text};
      }
      &.slick-active button:before {
        color: rgb(199, 8, 81);
      }
    }
  }
`;

export const ContentCard = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;   
  align-items: center;       
  flex-direction: column;
  padding: 20px;
  margin: 0 auto;
  text-align: center;
`;

export const PosterImage = styled.div`
  width: 87%;
  max-width: 100%;  
  padding-top: 60%;
  background-color: #ddd;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  transform-origin: center center;
  margin: 0 auto;
  position: relative;
  
  &:hover {
    transform: scale(1.02);
  }
  background-color: ${props => props.theme.cardBg};
  box-shadow: 0 4px 8px ${props => props.theme.shadow};
`;

export const ContentTitle = styled.h4`
  padding: 40px 0;
  margin: 0;
  text-align: center;
  font-size: 1.5rem;
  color: ${props => props.theme.text};
  width: 100%;
  position: relative;
  left: 0; 
`;

export const RecommendationSlider = styled(Slider)`
  width: 90%;
  margin: 0 auto;

  .slick-prev, .slick-next {
    width: 40px;
    height: 40px;
    z-index: 1;
    top: 40%;  // 상단으로 위치 조정
    &:before {
      font-size: 30px;
      color: rgba(199, 8, 81, 0.85);  // 투명도 증가로 더 옅은 색상
      opacity: 0.8;
    }
    &:hover:before {
      color: rgb(199, 8, 81);  // 호버시 원래 색상으로
      opacity: 1;
    }
  }
  
  .slick-prev {
    left: -45px;
  }
  
  .slick-next {
    right: -45px;
  }

  .slick-track {
    display: flex;
    gap: 20px;
  }

  .slick-slide {
    > div {
      margin: 0 10px;
    }
  }
`;

export const RecommendationSection = styled.section`
  padding: 30px 0;
  
  h2 {
    text-align: left;
    font-size: 2rem;
    color: ${props => props.theme.text};
    margin-bottom: 30px;
    padding-left: 60px;
  }
`;
  

export const PosterCard = styled.div`
  flex: 0 0 auto;
  width: 200px;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-5px);
  }
`;


export const SmallPosterImage = styled.div`
  width: 100%;
  padding-top: 150%; // 2:3 비율을 위해 width의 150%로 설정
  background-color: #ddd;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  background-image: url(${props => props.posterUrl});
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  position: relative;
  background-color: ${props => props.theme.cardBg};
  box-shadow: 0 4px 8px ${props => props.theme.shadow};
`;

export const SmallContentTitle = styled.h4`
  padding: 10px 0;
  margin: 0;
  text-align: center;
  font-size: 1rem;
  color: ${props => props.theme.text};
`;