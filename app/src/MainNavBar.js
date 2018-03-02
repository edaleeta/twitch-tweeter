import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Nav, NavItem } from 'react-bootstrap';

const navLinks = {
  home: "/",
  login: "/login/twitch",
  logout: "/logout",
  log: "/log"
}

// Navigation 
export class MainNavBar extends Component {
  // render() {
  //   return (
  //     <ul>
  //     <li><Link to={navLinks.home}>Home</Link></li>
  //     <li><a href={navLinks.login}>Login</a></li>
  //     <li><a href={navLinks.logout}>Logout</a></li>
  //     <li><Link to={navLinks.log}>Log</Link></li>
  //   </ul>
  //   );
  // }

  render() {
    return (
      <Navbar>
        <Navbar.Header>
          <Navbar.Brand>
            <Link to={navLinks.home}>Stream Tweeter</Link>
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Nav>
            <NavItem eventKey={1} href={navLinks.login}>
              Login
            </NavItem>
            <NavItem eventKey={2} href={navLinks.logout}>
              Logout
            </NavItem>
            <NavItem eventKey={3}
              componentClass={Link}
              href="/log"
              to="/log"
            >
              View Log
            </NavItem>
          </Nav>
          <Nav pullRight>
            <NavItem eventKey={4} href="#">
              Help
            </NavItem>
          </Nav>
        </Navbar.Collapse>
    </Navbar>
    );
  }

}