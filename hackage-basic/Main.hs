module Main where

import Data.Aeson (FromJSON, ToJSON, decode, encode, eitherDecode)
import Data.Aeson.Types (Value(..), object, (.=))
import qualified Data.ByteString.Lazy as BL
import qualified Data.ByteString.Lazy.Char8 as BLC
import qualified Data.Text as T
import System.Environment (getArgs)
import System.Process (readProcess)
import Network.HTTP.Client (newManager, parseRequest, httpLbs, responseBody, responseStatus)
import Network.HTTP.Client.TLS (tlsManagerSettings)
import Network.HTTP.Types.Status (statusCode)
import GHC.Generics (Generic)

data ServiceConfig = ServiceConfig
  { serviceName :: T.Text
  , servicePort :: Int
  , serviceHost :: T.Text
  , healthEndpoint :: T.Text
  } deriving (Show, Generic)

instance FromJSON ServiceConfig
instance ToJSON ServiceConfig

loadConfig :: FilePath -> IO (Either String ServiceConfig)
loadConfig path = do
  contents <- BL.readFile path
  return $ eitherDecode contents

checkServiceHealth :: ServiceConfig -> IO (Int, BL.ByteString)
checkServiceHealth config = do
  manager <- newManager tlsManagerSettings
  let url = T.unpack (serviceHost config)
          <> ":" <> show (servicePort config)
          <> T.unpack (healthEndpoint config)
  request <- parseRequest url
  response <- httpLbs request manager
  let status = statusCode (responseStatus response)
  return (status, responseBody response)

fetchRemoteConfig :: String -> IO (Either String Value)
fetchRemoteConfig url = do
  manager <- newManager tlsManagerSettings
  request <- parseRequest url
  response <- httpLbs request manager
  return $ eitherDecode (responseBody response)

runDiagnostic :: String -> [String] -> IO String
runDiagnostic cmd cmdArgs = readProcess cmd cmdArgs ""

buildReport :: ServiceConfig -> Int -> Value
buildReport config status = object
  [ "service" .= serviceName config
  , "port" .= servicePort config
  , "health_status" .= status
  , "healthy" .= (status == 200)
  ]

main :: IO ()
main = do
  args <- getArgs
  case args of
    [configPath] -> do
      result <- loadConfig configPath
      case result of
        Left err -> putStrLn $ "Config error: " <> err
        Right config -> do
          putStrLn $ "Checking " <> T.unpack (serviceName config)
          (status, _body) <- checkServiceHealth config
          let report = buildReport config status
          BLC.putStrLn (encode report)

    [configPath, "--remote-config", remoteUrl] -> do
      result <- loadConfig configPath
      case result of
        Left err -> putStrLn $ "Config error: " <> err
        Right config -> do
          remoteResult <- fetchRemoteConfig remoteUrl
          case remoteResult of
            Left err -> putStrLn $ "Remote config error: " <> err
            Right remoteVal -> do
              putStrLn "Remote config loaded"
              BLC.putStrLn (encode remoteVal)
              (status, _) <- checkServiceHealth config
              BLC.putStrLn (encode (buildReport config status))

    _ -> putStrLn "Usage: service-monitor <config.json> [--remote-config <url>]"
