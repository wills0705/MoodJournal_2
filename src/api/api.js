import api from './request';



const url = {
  generateTopic: '/associate_moods_with_topics'
}

const generateTopic = (text) => {
  return api.post(url.generateTopic, { text })
}

export {
  generateTopic,
}