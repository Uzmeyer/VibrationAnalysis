/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "i2c.h"
#include "spi.h"
#include "tim.h"
#include "usb_device.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "lsm6ds3.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint8_t string[] = "Hello World!\n\r";
char buffer[50];
uint16_t data[2000];
uint16_t recdata[12];
uint16_t lsmaddr = LSM6DS3_ADDRESS << 1;
int16_t x_val;
int16_t y_val;
int16_t z_val;
int n;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_I2C1_Init();
  MX_TIM1_Init();
  MX_USB_DEVICE_Init();
  MX_SPI1_Init();
  /* USER CODE BEGIN 2 */
  //HAL_Delay(5000);
  //HAL_I2C_Mem_Write(&hi2c1, lsmaddr, (uint16_t) 0x12, I2C_MEMADD_SIZE_8BIT, 0b00000100, 1, HAL_MAX_DELAY);
  HAL_I2C_Mem_Write(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_CTRL1_XL, I2C_MEMADD_SIZE_8BIT, 0b10100000, 1, HAL_MAX_DELAY);
  HAL_Delay(100);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	 /* HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTX_L_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  x_val = (recdata[0] & 0xFF);
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTX_H_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  x_val = (recdata[0] << 8) | x_val;
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTY_L_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  y_val = (recdata[0] & 0xFF);
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTY_H_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  y_val = (recdata[0] << 8) | y_val;
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTZ_L_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  z_val = (recdata[0] & 0xFF);
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTZ_H_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 1, HAL_MAX_DELAY);
	  z_val = (recdata[0] << 8) | z_val;
	  n = sprintf(buffer, "individual: %d, %d, %d\n",x_val,y_val,z_val);
	  CDC_Transmit_FS(buffer, n);
	  HAL_Delay(300); */
	  HAL_I2C_Mem_Read(&hi2c1, lsmaddr, (uint16_t) LSM6DS3_OUTX_L_XL, I2C_MEMADD_SIZE_8BIT, &recdata, 6, HAL_MAX_DELAY);
	  x_val = (recdata[0] & 0xFF ) | ((recdata[1] << 8));
	  y_val = (recdata[2] & 0xFF ) | ((recdata[3] << 8));
	  z_val = (recdata[4] & 0xFF ) | ((recdata[5] << 8));
	  n = sprintf(buffer, "bulk: %d, %d, %d\n",x_val,y_val,z_val);
	  CDC_Transmit_FS(buffer, n);
	  HAL_Delay(300);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);
  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
