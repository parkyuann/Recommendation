import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';

const SignupContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: ${props => props.theme.body};
  padding: 20px;
`;

const SignupBox = styled.div`
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

const SignupButton = styled.button`
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

const ErrorMessage = styled.p`
  color: #ff0000;
  font-size: 12px;
  margin: 4px 0;
`;

const LoginText = styled.div`
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

const SignupPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    birthdate: '',
    username: '',
    password: '',
    confirmPassword: '',
    phone: ''
  });
  const [passwordError, setPasswordError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  useEffect(() => {
    if (formData.password && formData.confirmPassword) {
      if (formData.password !== formData.confirmPassword) {
        setPasswordError('비밀번호가 일치하지 않습니다.');
      } else {
        setPasswordError('');
      }
    }
  }, [formData.password, formData.confirmPassword]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!passwordError) {
      // 회원가입 로직 구현
      console.log('회원가입 데이터:', formData);
      navigate('/login');
    }
  };

  return (
    <SignupContainer>
      <SignupBox>
        <Title>회원가입</Title>
        <form onSubmit={handleSubmit}>
          <Input
            type="text"
            name="name"
            placeholder="이름"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <Input
            type="date"
            name="birthdate"
            placeholder="생년월일"
            value={formData.birthdate}
            onChange={handleChange}
            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
            required
          />
          <Input
            type="text"
            name="username"
            placeholder="아이디"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <Input
            type="password"
            name="password"
            placeholder="비밀번호"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <Input
            type="password"
            name="confirmPassword"
            placeholder="비밀번호 확인"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
          {passwordError && <ErrorMessage>{passwordError}</ErrorMessage>}
          <Input
            type="tel"
            name="phone"
            placeholder="전화번호 (예: 010-1234-5678)"
            value={formData.phone}
            onChange={handleChange}
            pattern="[0-9]{3}-[0-9]{4}-[0-9]{4}"
            required
          />
          <SignupButton type="submit">가입하기</SignupButton>
        </form>
        <LoginText>
          이미 계정이 있으신가요?
          <Link to="/login">로그인</Link>
        </LoginText>
      </SignupBox>
    </SignupContainer>
  );
};

export default SignupPage;