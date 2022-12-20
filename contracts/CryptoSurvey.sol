// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;
pragma abicoder v2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract CryptoSurvey is Ownable, VRFConsumerBaseV2{
    using SafeERC20 for IERC20;
    IERC20 public cskToken;
    
    uint256 public signUpReward = 10 * (10 ** 18);
    mapping(address => user) userPool;
    uint256 public userSignUpCount;

    // Variable to ensure users does not malicously signup many accounts
    uint256 public signUpRewardLockTime = 1 days;
    uint256 public userSignUpCountLockLimit = 1000;
    uint256 public nextAccessTime;
    uint256 public userSignUpCountLockCount;
    uint256 public lastUserLimitTime;

    // for random number generation
    VRFCoordinatorV2Interface COORDINATOR;
    uint64 s_subscriptionId;

    // Goerli coordinator.
    address vrfCoordinator = 0x2Ca8E0C643bDe4C2E08ab1fA0da3401AdAD7734D;
    bytes32 s_keyHash =
        0x79d3d8832d904592c0bf9818b621522c988bb8b0c05cdc3b15aea1b6e8db0c15;
    uint16 requestConfirmations = 3;
    uint32 callbackGasLimit = 40000;
    uint32 numWords = 1;
    address s_owner;
    uint256[] public requestIds;
    uint256 public lastRequestId;
    uint256 private constant ROLL_IN_PROGRESS = 42;
    mapping(uint256 => uint256) private s_results;
    // end of random number variables 

    event Deposit(address indexed from, uint256 indexed amount);
    event Withdraw(address indexed to, uint256 indexed amount);
    event NumberRequested(uint256 indexed requestId);
    event NumberReturned(uint256 indexed requestId);

    struct user {
        uint256 dataQualityScore;
        bool isValue;
    }

    struct Survey {
        string name;
        bool isActive;
        uint256 reward;
        bool isLotto;
        uint256 enteranceFee;
        uint256 surveyEndTime;
        uint256 userCount;
        uint256 ranRequestId;
    }

    uint256 countSurveys=0;

    mapping(uint256 => Survey) private _surveys;
    mapping(uint256 => mapping(uint256 => address)) private _users;
    //surveyId->usersMapping    userId->user
    
    constructor(address tokenAddress, uint64 subscriptionId) VRFConsumerBaseV2(vrfCoordinator) {
        cskToken = IERC20(tokenAddress);
        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        s_owner = msg.sender;
        s_subscriptionId = subscriptionId;
    }

    // 
    function requestSignUpReward() public {
        require(msg.sender != address(0), "Address cannot be zero.");
        // require(cskToken.balanceOf(address(this)) >= signUpReward, "Insufficient token in CryptoSurvey contract");
        require(block.timestamp >  nextAccessTime, "Too many users signup.");
        require(userPool[msg.sender].isValue == false, "User already signup");
        
        userPool[msg.sender].dataQualityScore = 1;
        cskToken.transfer(msg.sender, signUpReward);

        // To prevent too many people from signing up to get the reward
        userSignUpCountLockCount += 1;

        if (userSignUpCountLockCount > userSignUpCountLockLimit){
            if (lastUserLimitTime + signUpRewardLockTime > block.timestamp) {
                nextAccessTime = block.timestamp + signUpRewardLockTime;
            }
            lastUserLimitTime = block.timestamp;
            userSignUpCountLockCount = 0;
        }
    }

    receive() external payable {
        emit Deposit(msg.sender, msg.value);
    }

    function getBalance() external view returns (uint256) {
        return cskToken.balanceOf(address(this));
    }

    function withdraw() external onlyOwner {
        emit Withdraw(msg.sender, cskToken.balanceOf(address(this)));
        cskToken.transfer(msg.sender, cskToken.balanceOf(address(this)));
    }

    function unlockSignUp() external onlyOwner {
        nextAccessTime = 0;
    }    

    function setLockTime(uint256 amtTime, uint256 amtUsers) public onlyOwner {
        signUpRewardLockTime = amtTime * 1 minutes;
        userSignUpCountLockLimit = amtUsers;
    }

    //get the number of surveys
    function getSurveyCount() public view returns (uint256) {

        return countSurveys;
    }

    //get the survey by id
    //ex: countSurveys=10 means there are ten surveys. the ids are 1,2,3,....10
    function getSurvey(uint256 id) external view returns (Survey memory){

        return _surveys[id];
    }

    //create a new survey, id is countSurveys+1
    function createSurvey(string memory pName, 
                        bool pIsLotto, 
                        uint256 pReward, 
                        uint256 surveyDuration, 
                        uint256 enteranceFee) public returns (uint256){
        countSurveys++;

        _surveys[countSurveys] = Survey({
            name: pName,
            isActive: true,
            reward: pReward,
            isLotto: pIsLotto,
            enteranceFee: enteranceFee,
            surveyEndTime: block.timestamp + surveyDuration * 1 minutes,
            userCount:0,
            ranRequestId:0
        });
        return countSurveys;
    }

    //report to a servey
    function report2Survey(uint256 surveyId) public {
        require(_surveys[surveyId].enteranceFee <= cskToken.balanceOf(msg.sender), "There is an entrance fee for this survey");
        require(block.timestamp <= _surveys[surveyId].surveyEndTime, "Survey has ended");
        address reporter = _msgSender();
        _surveys[surveyId].userCount++;
        uint256 uId=_surveys[surveyId].userCount;
        _users[surveyId][uId]=reporter;


        cskToken.safeIncreaseAllowance(reporter, _surveys[surveyId].reward);
    }


    //the owner of this contract can end the survey and give the reward
    function claimReward(uint256 surveyId) public onlyOwner{
        require(block.timestamp > _surveys[surveyId].surveyEndTime, "Survey has not ended");
        require(_surveys[surveyId].ranRequestId != 0, "please request random number for this survey" );
        require(s_results[_surveys[surveyId].ranRequestId] != ROLL_IN_PROGRESS, "Getting number in progress");

        if (_surveys[surveyId].isActive){
            if (_surveys[surveyId].isLotto){
                if (_surveys[surveyId].userCount!=0)
                {
                    uint256 uId= uint(s_results[_surveys[surveyId].ranRequestId] % _surveys[surveyId].userCount)+1;
                    address userAddress=_users[surveyId][uId];
                    uint256 amount=_surveys[surveyId].reward;
                
                    cskToken.transfer(userAddress, amount);
                }

            }else{
                uint256 amount=uint256(_surveys[surveyId].reward/_surveys[surveyId].userCount);
                for (uint i = 1; i <= _surveys[surveyId].userCount; i++) {
                    address userAddress=_users[surveyId][i];
                    
                    cskToken.transfer(userAddress, amount);
                }

            }
            _surveys[surveyId].isActive=false;
        }
    }

    function destroy() public onlyOwner {
        selfdestruct(payable(owner()));
    }

    function requestRandomNumberForSurvey(uint256 surveyId) public onlyOwner{
        require(_surveys[surveyId].ranRequestId == 0, "Random Number already requested");
        _surveys[surveyId].ranRequestId = requestRanNum();
    }


    function requestRanNum() public onlyOwner returns (uint256 requestId) {
        // Will revert if subscription is not set and funded.
        requestId = COORDINATOR.requestRandomWords(
            s_keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );

        requestIds.push(requestId);
        lastRequestId = requestId;

        s_results[requestId] = ROLL_IN_PROGRESS;
        emit NumberRequested(requestId);
    }


    function fulfillRandomWords(
        uint256 requestId,
        uint256[] memory randomWords
    ) internal override {
        s_results[requestId] = randomWords[0];
        emit NumberReturned(requestId);
    }

    function getInfo(uint requestId) public view returns (uint256) {
        require(s_results[requestId] != ROLL_IN_PROGRESS, "Getting number in progress");
        return s_results[requestId];
    }


}