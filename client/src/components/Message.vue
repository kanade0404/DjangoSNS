<template>
    <div>
      <h1>{{ msg }}</h1>
      <router-link to="/">ホーム</router-link>
      <router-link to="/sns">メッセージ</router-link>
      {{ messages }}
    </div>
</template>

<script>
  import axios from 'axios'
  export default {
    name: "Message",
    data(){
      return {
        msg: 'メッセージ',
        messages: ''
      }
    },
    mounted(){
      axios
        .get('/kanadesns/api/message').then(response => (this.messages = response))
    }
  }
</script>

<style scoped>

</style>
