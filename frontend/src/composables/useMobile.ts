import { Camera, CameraResultType, CameraSource } from '@capacitor/camera'
import { Filesystem, Directory } from '@capacitor/filesystem'
import { Share } from '@capacitor/share'
import { Haptics, ImpactStyle } from '@capacitor/haptics'
import { Toast } from '@capacitor/toast'
import { Capacitor } from '@capacitor/core'

export function useMobile() {
  const isNative = Capacitor.isNativePlatform()

  const takePhoto = async () => {
    try {
      if (isNative) {
        await Haptics.impact({ style: ImpactStyle.Light })
      }
      
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.DataUrl,
        source: CameraSource.Prompt,
        promptLabelHeader: 'Source de l\'image',
        promptLabelPhoto: 'Choisir dans la galerie',
        promptLabelPicture: 'Prendre une photo'
      })
      
      return image.dataUrl
    } catch (error) {
      console.error('Camera error:', error)
      return null
    }
  }

  const sharePDF = async (blob: Blob, filename: string) => {
    try {
      if (!isNative) {
        // Fallback browser download
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        return
      }

      // Capacitor logic for sharing
      const reader = new FileReader()
      reader.readAsDataURL(blob)
      reader.onloadend = async () => {
        const base64data = (reader.result as string).split(',')[1]
        
        // Save to temporary file
        const savedFile = await Filesystem.writeFile({
          path: filename,
          data: base64data,
          directory: Directory.Cache
        })

        await Share.share({
          title: filename,
          text: 'Consultez mon document Ventura',
          url: savedFile.uri,
          dialogTitle: 'Partager le PDF'
        })
      }
    } catch (error) {
      console.error('Share error:', error)
      await Toast.show({
        text: 'Erreur lors du partage du document'
      })
    }
  }

  const triggerHaptic = async (style: ImpactStyle = ImpactStyle.Medium) => {
    if (isNative) {
      await Haptics.impact({ style })
    }
  }

  const showToast = async (text: string) => {
    if (isNative) {
      await Toast.show({ text })
    } else {
      alert(text)
    }
  }

  return {
    isNative,
    takePhoto,
    sharePDF,
    triggerHaptic,
    showToast
  }
}
