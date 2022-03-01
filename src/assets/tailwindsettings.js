// CSS Options and Import
import {
  TButton,
  TInput,
  TTag,
  TRadio
} from 'vue-tailwind/dist/components'

const settings = {
  'desy-button': {
    component: TButton,
    props: {
      fixedClasses: 'block px-4 py-2 transition duration-100 ease-in-out focus:border-blue-500 focus:ring-2 focus:ring-desy-blue focus:outline-none focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed',
      classes: 'text-white bg-desy-blue border border-transparent shadow-sm rounded hover:bg-blue-600 focus:ring-red-500',
      variants: {
        secondary: 'text-gray-800 bg-white border border-gray-300 shadow-sm hover:text-gray-600',
        error: 'text-white bg-red-500 border border-transparent rounded shadow-sm hover:bg-red-600',
        success: 'text-white bg-green-500 border border-transparent rounded shadow-sm hover:bg-green-600',
        link: 'text-blue-500 underline hover:text-blue-600'
      }
    }
  },
  't-button': {
    component: TButton
  },
  't-input': {
    component: TInput
  },
  't-tag': {
    component: TTag,
    props: {
      fixedClasses: '',
      classes: '',
      variants: {
        radiolabel: 'flex w-1/6 justify-center border border-black bg-gray-100 rounded focus:ring-red-500'
      }
    }
  },
  't-radio': {
    component: TRadio,
    props: {
      classes: 'focus:border-desy-blue'
    }
  }
}

export default settings
