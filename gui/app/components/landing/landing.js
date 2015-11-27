'use strict';

angular.module('librarian')
    .controller('LandingController', [
      '$scope',
      '$route',
      '$rootScope',
      '$http',
      '$location',
      'VolumeService',

      function ($scope, $route, $rootScope, $http, $location, VolumeService) {
          $rootScope.isLanding = true;

          $scope.goTo = function(link) {
            $http({
                  method: 'GET',
                  url: '/check/traktor',
            }).then(function (response) {
                if(response.data.status == 'ok') {
                    $rootScope.isLanding = false;
                    $location.path(link);
                } else if (response.data.status == 'error') {
                    $rootScope.$emit('error', response.data.message);
                }
            });

          }

          var initialize = function() {
              VolumeService.getVolumes();
              $http({
                  method: 'GET',
                  url: '/init',
              }).then(function (data) {
              });
          }

          initialize();
    }]);


