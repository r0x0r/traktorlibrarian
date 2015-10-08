'use strict';

angular.module('librarian')
    .controller('LandingController', ['$scope', '$route', '$rootScope', '$http', '$location',
        function ($scope, $route, $rootScope, $http, $location) {
          $rootScope.isBackButtonVisible = false;

          $http({
            method: 'POST',
            url: '/',
            data: {
              action: 'initialize'
            }
          }).success(function (data, status, headers, config) {
            $rootScope.volumes = data.volumes;

            if (data.status == "error") {
              $rootScope.error = true;
              $rootScope.errorMessage = data.message;
            }
          });

          $scope.goTo = function(link) {
            $http({
              method: 'POST',
              url: '/',
              data: {
                action: 'check'
              }
            }).success(function (data) {
              if (data.status == "ok") {
                $location.path(link);
              } else if (data.status == "error") {
                $rootScope.error = true;
                $rootScope.errorMessage = data.message;
              }
            });

          }
    }]);


