import React, { useState } from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';

const LoginContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: ${props => props.theme.body};
`;

const LoginBox = styled.div`
  width: 400px;
  padding: 40px;
  background-color: ${props => props.theme.cardBg};
  border-radius: 10px;
  box-shadow: 0 4px 6px ${props => props.theme.shadow};
`;

const Title = styled.h1`
  text-align: center;
  color: ${props => props.theme.text};
  margin-bottom: 30px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid ${props => props.theme.headerBorder};
  border-radius: 4px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: rgb(199, 8, 81);
  }
`;

const LoginButton = styled.button`
  width: 100%;
  padding: 12px;
  margin: 20px 0;
  background-color: rgb(199, 8, 81);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;

  &:hover {
    background-color: rgba(199, 8, 81, 0.9);
  }
`;

const SignupText = styled.div`
  text-align: center;
  margin: 20px 0;
  color: ${props => props.theme.text};

  a {
    color: rgb(199, 8, 81);
    text-decoration: underline;
    margin-left: 8px;
    cursor: pointer;
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 20px 0;
  
  &::before, &::after {
    content: "";
    flex: 1;
    border-bottom: 1px solid ${props => props.theme.headerBorder};
  }
`;

const SocialButton = styled.button`
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid ${props => props.theme.headerBorder};
  border-radius: 4px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  &:hover {
    background-color: ${props => props.theme.hover};
  }

  img {
    width: 20px;
    height: 20px;
    margin-right: 10px;
  }
`;

const NaverButton = styled.button`
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: none;
  border-radius: 4px;
  background-color: #03C75A;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  &:hover {
    background-color: #02b351;
  }
`;

const KakaoButton = styled.button`
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: none;
  border-radius: 4px;
  background-color: #FEE500;
  color: #000000;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  &:hover {
    background-color: #f4dc00;
  }
`;

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // 로그인 로직 구현
    navigate('/main');
  };

  return (
    <LoginContainer>
      <LoginBox>
        <Title>로그인</Title>
        <form onSubmit={handleLogin}>
          <Input
            type="email"
            placeholder="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <LoginButton type="submit">로그인</LoginButton>
        </form>
        
        <SignupText>
          계정이 없으신가요?
          <Link to="/signup">회원가입</Link>
        </SignupText>

        <Divider />

        <NaverButton>
            <img src="/naver-icon.png" alt="naver" />
            네이버 아이디로 로그인
        </NaverButton>
        <SocialButton>
            <img src="/google-icon.png" alt="google" />
            구글로 로그인
        </SocialButton>
        <KakaoButton>
            <img src="/kakao-icon.png" alt="kakao" />
            카카오 아이디로 로그인
        </KakaoButton>
      </LoginBox>
    </LoginContainer>
  );
};

export default LoginPage;