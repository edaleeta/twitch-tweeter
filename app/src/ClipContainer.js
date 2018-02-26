import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Button } from 'react-bootstrap';
import { Clip } from './Clip'

export class ClipContainer extends Component {

  constructor(props) {
    super(props);
    this.state = {
      clipSlug: null,
    };
    this.handleOnLoadEmbed = this.handleOnLoadEmbed.bind(this);
  }

  componentWillMount() {
    // Fetch to get clip info.
  }

  handleOnLoadEmbed() {
    // Hide some spinner element when clip embed loads...
    console.log("Clip loaded!")
  }

  render() {
    return (
      <div> 
        <Clip
          clipSlug={this.state.clipSlug}
          hidden={this.props.clipHidden}
          onLoad={this.handleOnLoadEmbed}
        />
      </div>
    )
  }
}

ClipContainer.propTypes = {
  clipId: PropTypes.number,
  clipHidden: PropTypes.bool.isRequired
}